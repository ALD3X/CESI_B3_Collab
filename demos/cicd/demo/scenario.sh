#!/bin/sh
# Scénarios de démonstration : casser volontairement le pipeline pour montrer les quality gates.
# Usage (depuis la racine du dépôt de démo) :
#   sh demo/scenario.sh regression   -> erreur métier : les tests unitaires échouent
#   sh demo/scenario.sh secret       -> secret commité : gitleaks bloque
#   sh demo/scenario.sh reset        -> retour à l'état vert
# Puis : git commit -am "..." && git push  (GitHub)  /  le polling Jenkins détecte le commit en 1 min.
set -eu

case "${1:-}" in
  regression)
    # Un développeur passe par erreur la TVA normale de 20 % à 21 %.
    sed -i 's/TAUX_NORMAL = 0.20/TAUX_NORMAL = 0.21/' app/pricing.py
    echo "Régression injectée dans app/pricing.py (TVA 21 %). Attendu : étape tests ROUGE."
    ;;
  secret)
    # Un faux jeton d'accès est laissé dans un fichier de configuration.
    printf 'GITHUB_TOKEN = "ghp_%s"\n' "$(printf 'a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8')" > app/config.py
    echo "Faux secret ajouté dans app/config.py. Attendu : étape secrets ROUGE."
    ;;
  reset)
    sed -i 's/TAUX_NORMAL = 0.21/TAUX_NORMAL = 0.20/' app/pricing.py
    rm -f app/config.py
    echo "État vert restauré."
    ;;
  *)
    echo "Usage : sh demo/scenario.sh {regression|secret|reset}"
    exit 1
    ;;
esac
