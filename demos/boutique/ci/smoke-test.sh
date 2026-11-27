#!/bin/sh
# Test de bout en bout, commun aux deux pipelines : démarre TOUTE la boutique avec les images du build
# (front, passerelles, services, PostgreSQL, RabbitMQ) puis joue un parcours client (ci/smoke.py).
# Usage : sh ci/smoke-test.sh <nom-de-projet>
set -eu

PROJET="${1:-boutique-ci}"
DC="docker compose -p $PROJET -f docker-compose.yml -f ci/docker-compose.ci.yml --profile rabbit"

nettoyer() { $DC down -v --remove-orphans >/dev/null 2>&1 || true; }
trap nettoyer EXIT
nettoyer

echo "Démarrage de la boutique complète (projet $PROJET)..."
if ! $DC up -d --no-build --wait --wait-timeout 300; then
  echo "ÉCHEC : la boutique n'a pas démarré"
  $DC ps
  $DC logs --tail 40
  exit 1
fi

# Le parcours client s'exécute DANS le réseau de la boutique : aucun port publié sur la machine
docker run --rm -i --network "${PROJET}_default" python:3.12-alpine python - < ci/smoke.py
