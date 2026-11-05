import pytest

from app.main import app
from app.pricing import prix_ttc


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    rep = client.get("/health")
    assert rep.status_code == 200
    assert rep.get_json() == {"status": "ok"}


def test_liste_produits(client):
    rep = client.get("/api/produits")
    assert rep.status_code == 200
    assert len(rep.get_json()) == 3


def test_detail_produit_avec_ttc(client):
    rep = client.get("/api/produits/1")
    assert rep.status_code == 200
    assert rep.get_json()["prix_ttc"] == 59.88


def test_produit_inconnu(client):
    assert client.get("/api/produits/999").status_code == 404


@pytest.mark.parametrize(
    ("prix_ht", "categorie", "attendu"),
    [(100.0, "figurine", 120.0), (4.50, "fanzine", 4.59), (0.0, "film", 0.0)],
)
def test_prix_ttc(prix_ht, categorie, attendu):
    assert prix_ttc(prix_ht, categorie) == attendu


def test_prix_negatif_refuse():
    with pytest.raises(ValueError):
        prix_ttc(-1, "figurine")
