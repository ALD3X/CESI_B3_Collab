"""Règles de prix : TVA française selon la catégorie de produit."""

# Presse (fanzine) : taux super-réduit 2,1 % ; autres produits : taux normal 20 %.
TAUX_TVA = {"fanzine": 0.021}
TAUX_NORMAL = 0.20


def prix_ttc(prix_ht: float, categorie: str) -> float:
    if prix_ht < 0:
        raise ValueError("Le prix HT ne peut pas être négatif")
    taux = TAUX_TVA.get(categorie, TAUX_NORMAL)
    return round(prix_ht * (1 + taux), 2)
