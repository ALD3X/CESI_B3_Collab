"""Outils communs aux scénarios (bibliothèque standard uniquement)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import http.client as client_http
import json
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
import boutique  # noqa: E402  (pilotage docker compose et état courant)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SECRET_JWT = "demo-secret-petite-maison-epouvante-2026!"   # démo locale uniquement (docker-compose.yml)
MOT_DE_PASSE = "Epouvante2026!"
FRONT = 3000


# ---------- HTTP ----------
def http(methode: str, chemin: str, port: int = FRONT, jeton: str | None = None, corps=None,
         delai: float = 15) -> tuple[int, object, float]:
    conn = client_http.HTTPConnection("localhost", port, timeout=delai)
    entetes = {"Content-Type": "application/json"}
    if jeton:
        entetes["Authorization"] = f"Bearer {jeton}"
    debut = time.perf_counter()
    conn.request(methode, chemin, body=None if corps is None else json.dumps(corps), headers=entetes)
    rep = conn.getresponse()
    texte = rep.read().decode(errors="replace")
    duree = time.perf_counter() - debut
    conn.close()
    try:
        return rep.status, json.loads(texte) if texte else None, duree
    except json.JSONDecodeError:
        return rep.status, texte.strip(), duree


def connexion(membre: str = "morticia", port: int = FRONT) -> str:
    statut, corps, _ = http("POST", "/api/identite/connexion", port,
                            corps={"email": f"{membre}@petitemaison.fr", "motDePasse": MOT_DE_PASSE})
    if statut != 200:
        raise RuntimeError(f"Connexion impossible ({statut}) : la boutique est-elle démarrée ?")
    return corps["jeton"]


def commander(jeton: str, produit: int = 1, port: int = FRONT) -> int:
    return http("POST", "/api/commandes", port, jeton, {"lignes": [{"produitId": produit, "quantite": 1}]})[0]


def stats(service: str, port: int = FRONT) -> dict:
    return http("GET", f"/api/{service}/stats", port)[1]


# ---------- Jetons forgés (scénario sécurité) ----------
def _b64(donnees: bytes) -> str:
    return base64.urlsafe_b64encode(donnees).rstrip(b"=").decode()


def jeton_forge(secret: str = SECRET_JWT, expire_dans: int = 300, sujet: str = "morticia@petitemaison.fr") -> str:
    entete = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    maintenant = int(time.time())
    charge = _b64(json.dumps({"iss": "petite-maison", "sub": sujet, "iat": maintenant,
                              "exp": maintenant + expire_dans}).encode())
    signature = hmac.new(secret.encode(), f"{entete}.{charge}".encode(), hashlib.sha256).digest()
    return f"{entete}.{charge}.{_b64(signature)}"


# ---------- Docker ----------
def etat() -> dict:
    return boutique.lire_etat()


def compose(*args: str, profils: tuple[str, ...] = (), env: dict | None = None) -> None:
    e = boutique.environnement(etat())
    e.update(env or {})
    commande = ["docker", "compose"]
    for p in (etat()["bus"], *profils):
        commande += ["--profile", p]
    subprocess.run([*commande, *args], cwd=RACINE, env=e, check=True, capture_output=True)


def docker(*args: str) -> str:
    return subprocess.run(["docker", *args], check=True, capture_output=True, text=True).stdout.strip()


def attendre(condition, delai: float = 30, pas: float = 0.3):
    """Répète condition() jusqu'à obtenir une valeur vraie ou dépasser le délai ; renvoie la dernière valeur."""
    fin = time.perf_counter() + delai
    valeur = condition()
    while not valeur and time.perf_counter() < fin:
        time.sleep(pas)
        valeur = condition()
    return valeur


# ---------- Affichage ----------
class Verifications:
    def __init__(self) -> None:
        self.resultats: list[bool] = []

    def verifier(self, libelle: str, condition: bool, detail: str = "") -> None:
        self.resultats.append(condition)
        print(f"   {'✅' if condition else '❌'} {libelle}" + (f"  ({detail})" if detail else ""))

    def bilan(self, nom: str) -> int:
        ok = sum(self.resultats)
        print(f"\n{'✅' if ok == len(self.resultats) else '⚠️ '} {nom} : {ok}/{len(self.resultats)} vérifications réussies")
        return 0 if ok == len(self.resultats) else 1


def etape(titre: str, pause: bool = False) -> None:
    if pause:
        input("\n⏎  Entrée pour continuer…")
    print(f"\n━━ {titre}")
