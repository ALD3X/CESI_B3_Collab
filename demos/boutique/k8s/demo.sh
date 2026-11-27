#!/usr/bin/env sh
# Démo EPIC 06 (US-06.1) — La boutique sur Kubernetes : architecture interne observée en direct.
# Usage : [ENV=prod|accp] sh k8s/demo.sh preparer | composants | deployer | ouvrir | auto-reparation | mise-a-jour | cloisonnement | nettoyer
# ENV (prod par défaut) choisit l'environnement montré : namespaces prod-* ou accp-*.
set -e
PROFIL=boutique
ENV="${ENV:-prod}"
K="kubectl --context $PROFIL"
ICI=$(cd "$(dirname "$0")" && pwd)
APP="$K -n $ENV-applicative"
IMAGES="boutique-front boutique-passerelle boutique-identite boutique-catalogue boutique-commandes \
boutique-notifications boutique-expedition boutique-postgres"

etape() { printf '\n━━━ %s\n' "$1"; }

case "${1:-}" in
  preparer)
    etape "Cluster local : 1 nœud control plane + 1 nœud worker (la veille : environ 5 min)"
    minikube start -p "$PROFIL" --nodes 2 --driver docker --memory 3500 --cpus 2 --addons metrics-server
    etape "Images de la boutique (celles du pipeline CI/CD) chargées dans le cluster"
    (cd "$ICI/.." && docker compose build -q)
    for image in $IMAGES; do
      echo "  → $image"
      minikube -p "$PROFIL" image load "$image:latest"
    done
    for image in rabbitmq:3.13-management redis:7.4-alpine curlimages/curl:8.11.1; do
      docker pull -q "$image" >/dev/null && minikube -p "$PROFIL" image load "$image"
    done
    ;;
  composants)
    etape "Les nœuds : rôle control-plane et worker"
    $K get nodes -o wide
    etape "Le control plane et les agents de nœud tournent eux-mêmes comme des pods (namespace kube-system)"
    $K get pods -n kube-system -o custom-columns=COMPOSANT:.metadata.name,NOEUD:.spec.nodeName,ETAT:.status.phase
    etape "L'API server est le point d'entrée unique : tout passe par lui"
    $K cluster-info
    ;;
  deployer)
    etape "État souhaité de l'environnement $ENV (Kustomize) : kubectl apply → API server → etcd"
    etape "Le scheduler place les pods, le kubelet de chaque nœud démarre les conteneurs, puis test de fumée"
    kubectl config use-context "$PROFIL" >/dev/null
    (cd "$ICI/.." && TAG=latest CHARGER_IMAGES=minikube:$PROFIL sh ci/deployer.sh "$ENV")
    etape "La boutique en $ENV : 3 zones, chaque service redondé ou relancé automatiquement"
    $K get pods -A -l 'app' -o custom-columns=ZONE:.metadata.namespace,POD:.metadata.name,NOEUD:.spec.nodeName,ETAT:.status.phase \
      | grep -E "ZONE|$ENV-"
    ;;
  ouvrir)
    etape "Boutique servie par Kubernetes : http://localhost:3001  (Ctrl+C pour arrêter)"
    $K -n "$ENV-publique" port-forward svc/front 3001:80
    ;;
  auto-reparation)
    POD=$($APP get pods -l app=catalogue -o jsonpath='{.items[0].metadata.name}')
    etape "Suppression brutale de l'instance $POD du catalogue (simule une panne)"
    $APP delete pod "$POD" --wait=false
    etape "Le controller manager constate l'écart (1 instance au lieu de 2) et en recrée une"
    sleep 2
    $APP get pods -l app=catalogue -o wide
    $APP rollout status deploy/catalogue --timeout=120s
    $APP get events --sort-by=.lastTimestamp | grep -i catalogue | tail -n 6
    ;;
  mise-a-jour)
    etape "Mise à l'échelle à 4 instances du catalogue (le HPA ferait de même sous charge)"
    $APP scale deploy/catalogue --replicas=4
    $APP rollout status deploy/catalogue --timeout=180s
    $APP get pods -l app=catalogue -o wide
    etape "Redémarrage progressif (rolling update) : aucune coupure de service"
    $APP rollout restart deploy/catalogue
    $APP rollout status deploy/catalogue --timeout=300s
    $APP scale deploy/catalogue --replicas=2
    ;;
  cloisonnement)
    SONDE="--rm -i --restart=Never --image=curlimages/curl:8.11.1 --image-pull-policy=IfNotPresent --"
    etape "Depuis la zone applicative vers le catalogue : autorisé"
    $APP run sonde-applicative $SONDE -s -m 5 -o /dev/null -w "code HTTP : %{http_code}\n" \
      http://catalogue:8080/api/catalogue/produits/1 || true
    etape "Depuis la zone publique vers la passerelle : autorisé (chemin normal du front)"
    $K -n "$ENV-publique" run sonde-publique $SONDE -s -m 5 -o /dev/null -w "code HTTP : %{http_code}\n" \
      http://passerelle.$ENV-applicative:8080/api/catalogue/produits/1 || true
    etape "Depuis la zone publique DIRECTEMENT vers le catalogue : bloqué (contournement de la passerelle)"
    $K -n "$ENV-publique" run sonde-contournement $SONDE -s -m 5 -o /dev/null \
      -w "code HTTP : %{http_code} (000 = aucune réponse)\n" \
      http://catalogue.$ENV-applicative:8080/api/catalogue/produits/1 || true
    etape "Depuis la zone publique vers la base de données : bloqué"
    $K -n "$ENV-publique" run sonde-donnees $SONDE -s -m 5 -o /dev/null \
      -w "code : %{http_code} (000 = aucune réponse)\n" telnet://postgres.$ENV-donnees:5432 || true
    etape "Depuis la RECETTE vers la base de PRODUCTION : bloqué (environnements isolés)"
    $K -n accp-applicative run sonde-inter-env $SONDE -s -m 5 -o /dev/null \
      -w "code : %{http_code} (000 = aucune réponse)\n" telnet://postgres.prod-donnees:5432 || true
    ;;
  nettoyer)
    $K delete ns "$ENV-publique" "$ENV-applicative" "$ENV-donnees" --ignore-not-found
    minikube stop -p "$PROFIL"
    ;;
  *)
    echo "Usage : sh k8s/demo.sh preparer | composants | deployer | ouvrir | auto-reparation | mise-a-jour | cloisonnement | nettoyer"
    exit 1
    ;;
esac
