#!/bin/sh
# Déploiement GitOps par Argo CD (chaîne Jenkins + Argo CD), puis test de fumée.
#   sh infra/ci/deployer-argocd.sh accp   → application boutique-accp (synchronisation automatique)
#   sh infra/ci/deployer-argocd.sh prod   → application boutique-prod (synchronisation manuelle), RETOUR ARRIÈRE
#                                           par l'historique d'Argo CD en cas d'échec
#
# Différence avec infra/ci/deployer.sh (GitHub Actions, modèle « push ») : le pipeline n'applique rien dans le
# cluster et n'en possède aucun accès. Il indique à Argo CD la version des images, et c'est Argo CD, dans le
# cluster, qui applique l'état décrit dans Git (branche accp ou prod, surcouche Kustomize).
#
# Variables : REGISTRE et TAG (images à déployer, ex. TAG=v-<version>)
#             ARGOCD_SERVER et ARGOCD_AUTH_TOKEN (sinon lus dans /var/jenkins_home/argocd.env, créé par
#             infra/argocd/installer.sh) ; CHARGER_IMAGES = minikube:<profil> (registre local inaccessible au cluster)
set -eu
cd "$(dirname "$0")/../.."

ENV="${1:?environnement : accp ou prod}"
R="${REGISTRE:-}"
TAG="${TAG:?version des images à déployer}"
IMAGES="front passerelle identite catalogue commandes notifications expedition postgres"
APP="boutique-$ENV"

FICHIER_ARGOCD="${ARGOCD_ENV:-/var/jenkins_home/argocd.env}"
if [ -z "${ARGOCD_AUTH_TOKEN:-}" ] && [ -f "$FICHIER_ARGOCD" ]; then . "$FICHIER_ARGOCD"; fi
: "${ARGOCD_SERVER:?serveur Argo CD inconnu : lancer « npm run argocd:installer »}"
: "${ARGOCD_AUTH_TOKEN:?jeton Argo CD absent : lancer « npm run argocd:installer »}"
argocd_() { argocd --server "$ARGOCD_SERVER" --auth-token "$ARGOCD_AUTH_TOKEN" --insecure --grpc-web "$@"; }

case "$ENV" in accp|prod) ;; *) echo "Environnement inconnu : $ENV (accp ou prod)"; exit 1 ;; esac

# 1. Images disponibles dans le cluster (cluster local : chargées dans chaque nœud minikube)
case "${CHARGER_IMAGES:-}" in
  minikube:*)
    profil="${CHARGER_IMAGES#minikube:}"
    for noeud in $(docker ps --filter "name=^${profil}(-m[0-9]+)?$" --format '{{.Names}}'); do
      for i in $IMAGES; do
        docker save "${R}boutique-$i:$TAG" | docker exec -i "$noeud" ctr -n k8s.io images import - >/dev/null
      done
    done ;;
esac

# 2. Version des images transmise à Argo CD, puis synchronisation avec Git
echo "Argo CD : $APP ← ${R}boutique-*:$TAG (état souhaité : branche $ENV, infra/k8s/overlays/$ENV)"
set --
for i in $IMAGES; do set -- "$@" --kustomize-image "boutique-$i=${R}boutique-$i:$TAG"; done
argocd_ app set "$APP" "$@"

ok=1
# accp : synchronisation automatique, Argo CD applique seul le changement ; prod : synchronisation explicite
if [ "$ENV" = "prod" ]; then argocd_ app sync "$APP" --timeout 600 >/dev/null || ok=0; fi

# Attendre que les ressources du cluster portent la nouvelle version (sinon l'attente suivante verrait
# l'état « sain » de l'ancienne version), puis que le déploiement progressif soit terminé et sain
if [ "$ok" -eq 1 ]; then
  n=0
  until argocd_ app get "$APP" -o json | grep -q "\"${R}boutique-front:$TAG\""; do
    n=$((n + 1)); [ "$n" -gt 60 ] && { echo "Argo CD n'a pas appliqué la version $TAG."; ok=0; break; }
    sleep 5
  done
fi
[ "$ok" -eq 1 ] && { argocd_ app wait "$APP" --sync --health --timeout 600 >/dev/null || ok=0; }

# 3. Test de fumée depuis le réseau du cluster (front exposé sur le port du nœud : accp 30081, prod 30080)
if [ "$ok" -eq 1 ]; then
  port=30081; [ "$ENV" = "prod" ] && port=30080
  docker run --rm -i --network "${RESEAU_CLUSTER:-boutique}" -e "FRONT=http://${ARGOCD_SERVER%%:*}:$port" -e KONG= \
    python:3.12-alpine python - < infra/ci/smoke.py || ok=0
fi

if [ "$ok" -ne 1 ]; then
  echo "ÉCHEC du déploiement $ENV."
  if [ "$ENV" = "prod" ]; then
    echo "Retour arrière par Argo CD vers la version précédente de son historique…"
    argocd_ app rollback "$APP" || true
  fi
  exit 1
fi
echo "Environnement $ENV synchronisé par Argo CD et vérifié."
