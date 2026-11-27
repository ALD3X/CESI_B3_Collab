#!/bin/sh
# Contrôles de sécurité du code, communs aux deux pipelines et au poste du développeur.
#   sh infra/ci/controles-securite.sh secrets   → gitleaks : secret dans le code (bloquant)
#   sh infra/ci/controles-securite.sh sast      → Semgrep : analyse statique, bloquant si sévérité ERROR
#   sh infra/ci/controles-securite.sh sca       → Trivy : dépendances Maven et npm, bloquant si CRITIQUE corrigeable
# Si l'outil est installé (étapes Jenkins exécutées dans l'image de l'outil), il est lancé directement ;
# sinon, il est lancé dans son image Docker officielle.
set -eu
cd "$(dirname "$0")/../.."

GITLEAKS_IMAGE="${GITLEAKS_IMAGE:-zricethezav/gitleaks:v8.24.3}"
SEMGREP_IMAGE="${SEMGREP_IMAGE:-semgrep/semgrep:1.99.0}"
TRIVY_IMAGE="${TRIVY_IMAGE:-aquasec/trivy:0.65.0}"
# Chemin du dépôt tel que Docker le comprend (pwd -W : format Windows sous Git Bash)
SRC=$(pwd -W 2>/dev/null || pwd)

controle="${1:-}"
case "$controle" in
  secrets)
    if command -v gitleaks >/dev/null 2>&1; then
      gitleaks dir . --no-banner --redact
    else
      docker run --rm -v "$SRC:/src" "$GITLEAKS_IMAGE" dir /src --no-banner --redact
    fi
    ;;
  sast)
    set -- --config p/java --config p/react --config p/secrets --severity ERROR --error --metrics off \
      --exclude "**/target" --exclude node_modules
    if command -v semgrep >/dev/null 2>&1; then
      semgrep scan "$@" .
    else
      docker run --rm -v "$SRC:/src" -w /src "$SEMGREP_IMAGE" semgrep scan "$@" .
    fi
    ;;
  sca)
    set -- fs --quiet --scanners vuln --severity CRITICAL --ignore-unfixed --skip-dirs "**/node_modules" --exit-code 1
    if command -v trivy >/dev/null 2>&1; then
      trivy "$@" .
    else
      docker run --rm -v "$SRC:/src" -v trivy-cache:/root/.cache "$TRIVY_IMAGE" "$@" /src
    fi
    ;;
  *)
    echo "Usage : sh infra/ci/controles-securite.sh secrets | sast | sca"
    exit 1
    ;;
esac
