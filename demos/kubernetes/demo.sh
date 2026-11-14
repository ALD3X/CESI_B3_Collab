#!/usr/bin/env sh
# Démo EPIC 06 (US-06.1) — Architecture interne de Kubernetes, observée en direct.
# Usage : sh demo.sh preparer | composants | deployer | auto-reparation | mise-a-jour | cloisonnement | nettoyer
set -e
PROFIL=petite-maison
NS=zone-applicative
K="kubectl --context $PROFIL"
ICI=$(cd "$(dirname "$0")" && pwd)

etape() { printf '\n━━━ %s\n' "$1"; }

case "${1:-}" in
  preparer)
    etape "Cluster local : 1 nœud control plane + 1 nœud worker"
    minikube start -p "$PROFIL" --nodes 2 --driver docker --memory 2200 --cpus 2 --addons metrics-server
    etape "Image du catalogue (même Dockerfile que la démo CI/CD) chargée dans le cluster"
    docker build -q -t petite-maison/catalogue:1.0.0 "$ICI/../cicd"
    minikube -p "$PROFIL" image load petite-maison/catalogue:1.0.0
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
    etape "État souhaité déclaré dans un fichier versionné (kubectl apply → API server → etcd)"
    $K apply -f "$ICI/catalogue.yaml"
    $K -n "$NS" rollout status deploy/catalogue --timeout=120s
    etape "Le scheduler a placé les 2 instances (de préférence sur des nœuds différents)"
    $K -n "$NS" get pods -o wide
    $K -n "$NS" get svc,hpa,pdb
    ;;
  auto-reparation)
    POD=$($K -n "$NS" get pods -l app=catalogue -o jsonpath='{.items[0].metadata.name}')
    etape "Suppression brutale de l'instance $POD (simule une panne)"
    $K -n "$NS" delete pod "$POD" --wait=false
    etape "Le controller manager constate l'écart (1 instance au lieu de 2) et en recrée une"
    sleep 2
    $K -n "$NS" get pods -o wide
    $K -n "$NS" rollout status deploy/catalogue --timeout=60s
    $K -n "$NS" get events --sort-by=.lastTimestamp | tail -n 8
    ;;
  mise-a-jour)
    etape "Mise à l'échelle manuelle à 4 instances (le HPA ferait de même automatiquement sous charge)"
    $K -n "$NS" scale deploy/catalogue --replicas=4
    $K -n "$NS" rollout status deploy/catalogue --timeout=60s
    $K -n "$NS" get pods -o wide
    etape "Redémarrage progressif (rolling update) : aucune coupure de service"
    $K -n "$NS" rollout restart deploy/catalogue
    $K -n "$NS" rollout status deploy/catalogue --timeout=120s
    $K -n "$NS" scale deploy/catalogue --replicas=2
    ;;
  cloisonnement)
    etape "Appel depuis la zone applicative : autorisé par la NetworkPolicy"
    $K -n "$NS" run sonde-interne --rm -i --restart=Never --image=curlimages/curl:8.11.1 -- \
      -s -m 5 http://catalogue/api/produits/1 || true
    etape "Appel depuis un autre namespace : bloqué (délai dépassé)"
    $K -n default run sonde-externe --rm -i --restart=Never --image=curlimages/curl:8.11.1 -- \
      -s -m 5 -o /dev/null -w "code HTTP : %{http_code} (000 = aucune réponse)\n" \
      http://catalogue.zone-applicative/health || true
    ;;
  nettoyer)
    $K delete -f "$ICI/catalogue.yaml" --ignore-not-found
    minikube stop -p "$PROFIL"
    ;;
  *)
    echo "Usage : sh demo.sh preparer | composants | deployer | auto-reparation | mise-a-jour | nettoyer"
    exit 1
    ;;
esac
