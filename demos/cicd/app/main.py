"""Mini-service « catalogue » de démonstration pour la Petite Maison de l'Épouvante.

Ce n'est PAS l'e-commerce : c'est un service volontairement minimal qui sert
de support identique aux deux pipelines CI/CD comparés (GitHub Actions / Jenkins).
"""

from flask import Flask, abort, jsonify

from app.pricing import prix_ttc

app = Flask(__name__)

PRODUITS = {
    1: {"id": 1, "nom": "Figurine L'Orc (exclusivité Evil Ed)", "prix_ht": 49.90, "categorie": "figurine"},
    2: {"id": 2, "nom": "Fanzine n°38 (numérique)", "prix_ht": 4.50, "categorie": "fanzine"},
    3: {"id": 3, "nom": "Blu-ray Riflesso di un coltello nella notte", "prix_ht": 24.99, "categorie": "film"},
}


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/api/produits")
def lister_produits():
    return jsonify([_avec_ttc(p) for p in PRODUITS.values()])


@app.get("/api/produits/<int:produit_id>")
def detail_produit(produit_id: int):
    produit = PRODUITS.get(produit_id)
    if produit is None:
        abort(404)
    return jsonify(_avec_ttc(produit))


def _avec_ttc(produit: dict) -> dict:
    return {**produit, "prix_ttc": prix_ttc(produit["prix_ht"], produit["categorie"])}


if __name__ == "__main__":  # pragma: no cover
    # Écoute sur toutes les interfaces : nécessaire dans un conteneur.
    app.run(host="0.0.0.0", port=8000)  # nosec B104
