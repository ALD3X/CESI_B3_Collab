#!/bin/sh
# Smoke test commun aux deux pipelines : démarre l'image et vérifie qu'elle répond.
# Usage : ci/smoke-test.sh <image:tag> <nom-conteneur>
set -eu

IMAGE="$1"
NAME="$2"
CURL="curlimages/curl:8.11.1"

docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" "$IMAGE" >/dev/null
trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT

echo "Attente du démarrage de $NAME..."
i=0
until docker run --rm --network "container:$NAME" "$CURL" -fsS http://localhost:8000/health >/dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -ge 15 ]; then
    echo "ÉCHEC : le service ne répond pas sur /health"
    docker logs "$NAME" || true
    exit 1
  fi
  sleep 2
done

echo "Service démarré. Vérification de l'API catalogue :"
docker run --rm --network "container:$NAME" "$CURL" -fsS http://localhost:8000/api/produits/1
echo
echo "Smoke test OK"
