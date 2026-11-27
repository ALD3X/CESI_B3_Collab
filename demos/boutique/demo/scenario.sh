#!/bin/sh
# Scénarios « pipeline rouge » : casser volontairement le pipeline pour montrer les quality gates.
# Usage (depuis la racine du dépôt de la boutique) :
#   sh demo/scenario.sh regression   -> erreur métier : les tests du service catalogue échouent
#   sh demo/scenario.sh secret       -> secret commité : gitleaks bloque
#   sh demo/scenario.sh reset        -> retour à l'état vert
# Puis : git commit -am "..." && git push (GitHub)  /  le polling Jenkins détecte le commit en 1 min.
set -eu

TARIF=backend/catalogue/src/main/java/fr/petitemaison/catalogue/Tarification.java
CONFIG=backend/commandes/src/main/resources/paiement.properties

case "${1:-}" in
  regression)
    # Un développeur passe par erreur la TVA normale de 20 % à 21 %.
    sed -i 's/new BigDecimal("0.20")/new BigDecimal("0.21")/' "$TARIF"
    echo "Régression injectée dans $TARIF (TVA 21 %). Attendu : étape backend ROUGE."
    ;;
  secret)
    # Une clé d'API du prestataire de paiement est laissée dans un fichier de configuration.
    printf 'paiement.cle-api=sk_live_%s\n' "$(printf '4eC39HqLyjWDarjtT1zdp7dcX9bQ2mN8')" > "$CONFIG"
    echo "Faux secret ajouté dans $CONFIG. Attendu : étape secrets ROUGE."
    ;;
  reset)
    sed -i 's/new BigDecimal("0.21")/new BigDecimal("0.20")/' "$TARIF"
    rm -f "$CONFIG"
    echo "État vert restauré."
    ;;
  *)
    echo "Usage : sh demo/scenario.sh {regression|secret|reset}"
    exit 1
    ;;
esac
