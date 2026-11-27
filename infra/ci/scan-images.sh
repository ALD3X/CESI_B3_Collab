#!/bin/sh
# Scan des images construites, commun aux deux pipelines.
# Bloquant si une vulnérabilité CRITIQUE disposant d'un correctif est trouvée, sauf exception
# justifiée et datée dans .trivyignore.yaml (registre des risques acceptés).
set -eu
cd "$(dirname "$0")/../.."

TRIVY_IMAGE="${TRIVY_IMAGE:-aquasec/trivy:0.65.0}"
statut=0
for image in $(docker compose -f infra/compose/compose.yaml config --images | grep "boutique-" | sort -u); do
  echo "== Scan de $image"
  # Le registre des exceptions est transmis par l'entrée standard : aucun montage de fichier
  # (indispensable quand Jenkins pilote Docker depuis son propre conteneur)
  docker run --rm -i -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache \
    --entrypoint sh "$TRIVY_IMAGE" -c "cat > /tmp/exceptions.yaml && trivy image --quiet \
      --severity CRITICAL --ignore-unfixed --ignorefile /tmp/exceptions.yaml --exit-code 1 $image" \
    < .trivyignore.yaml || statut=1
done
if [ "$statut" -eq 0 ]; then
  echo "Aucune vulnérabilité critique corrigeable (hors exceptions documentées)."
else
  echo "ÉCHEC : vulnérabilité critique corrigeable."
fi
exit "$statut"
