#!/bin/sh
# Déploiement d'un environnement puis test de fumée, commun aux deux pipelines.
#   sh ci/deployer.sh dev    → Docker Compose (projet boutique-dev, front sur le port 3100)
#   sh ci/deployer.sh accp   → Kubernetes, namespaces accp-*, iso-production avec 1 instance par service
#   sh ci/deployer.sh prod   → Kubernetes, namespaces prod-*, 2 instances, RETOUR ARRIÈRE automatique si échec
#
# Variables : REGISTRE et TAG (images à déployer, ex. TAG=v-<version>)
#             CHARGER_IMAGES = minikube:<profil> | kind:<cluster> | (vide : le cluster tire les images du registre)
set -eu
cd "$(dirname "$0")/.."

ENV="${1:?environnement : dev, accp ou prod}"
R="${REGISTRE:-}"
TAG="${TAG:?version des images à déployer}"
IMAGES="front passerelle identite catalogue commandes notifications expedition postgres"

test_de_fumee_k8s() {
  kubectl -n "$ENV-publique" delete pod fumee --ignore-not-found >/dev/null
  kubectl -n "$ENV-publique" run fumee --rm -i --restart=Never --image=python:3.12-alpine \
    --image-pull-policy=IfNotPresent --env=FRONT=http://front --env=KONG= -- python - < ci/smoke.py
}

case "$ENV" in
  dev)
    DC="docker compose -p boutique-dev -f docker-compose.yml -f deploy/dev.yml --profile rabbit"
    echo "Déploiement dev : ${R}boutique-*:$TAG (Docker Compose)"
    $DC up -d --no-build --wait --wait-timeout 300
    docker run --rm -i --network boutique-dev_default -e FRONT=http://front:8080 python:3.12-alpine \
      python - < ci/smoke.py
    echo "Environnement dev disponible : http://localhost:3100"
    ;;

  accp|prod)
    # 1. Images disponibles pour le cluster
    case "${CHARGER_IMAGES:-}" in
      minikube:*)
        for i in $IMAGES; do
          for noeud in $(kubectl get nodes -o name | cut -d/ -f2); do
            docker save "${R}boutique-$i:$TAG" | docker exec -i "$noeud" ctr -n k8s.io images import - >/dev/null
          done
        done ;;
      kind:*)
        for i in $IMAGES; do kind load docker-image "${R}boutique-$i:$TAG" --name "${CHARGER_IMAGES#kind:}"; done ;;
    esac

    # 2. Application de l'état souhaité (surcouche Kustomize de l'environnement)
    echo "Déploiement $ENV : ${R}boutique-*:$TAG (Kubernetes)"
    kubectl kustomize "k8s/overlays/$ENV" \
      | sed -E "s#image: boutique-([a-z]+):latest#image: ${R}boutique-\\1:$TAG#" \
      | kubectl apply -f -

    # 3. Attente du déploiement progressif, puis test de fumée
    ok=1
    kubectl -n "$ENV-donnees" rollout status statefulset/postgres --timeout=300s || ok=0
    kubectl -n "$ENV-donnees" rollout status deploy/rabbitmq --timeout=300s || ok=0
    for d in passerelle identite catalogue commandes notifications expedition; do
      kubectl -n "$ENV-applicative" rollout status "deploy/$d" --timeout=420s || ok=0
    done
    kubectl -n "$ENV-publique" rollout status deploy/front --timeout=180s || ok=0
    [ "$ok" -eq 1 ] && test_de_fumee_k8s || ok=0

    if [ "$ok" -ne 1 ]; then
      echo "ÉCHEC du déploiement $ENV."
      if [ "$ENV" = "prod" ]; then
        echo "Retour arrière automatique vers la version précédente…"
        for d in passerelle identite catalogue commandes notifications expedition; do
          kubectl -n prod-applicative rollout undo "deploy/$d" || true
        done
        kubectl -n prod-publique rollout undo deploy/front || true
      fi
      exit 1
    fi
    echo "Environnement $ENV déployé et vérifié."
    ;;

  *)
    echo "Environnement inconnu : $ENV (dev, accp ou prod)"
    exit 1
    ;;
esac
