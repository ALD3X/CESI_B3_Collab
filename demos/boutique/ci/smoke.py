"""Parcours client de bout en bout (exécuté dans le réseau de la boutique par ci/smoke-test.sh)."""

import json
import sys
import time
import urllib.error
import urllib.request

FRONT = "http://front:8080"          # front → passerelle Spring Cloud Gateway
KONG = "http://kong:8000"            # seconde passerelle
echecs = 0


def appel(url, corps=None, jeton=None):
    entetes = {"Content-Type": "application/json"}
    if jeton:
        entetes["Authorization"] = "Bearer " + jeton
    req = urllib.request.Request(url, data=json.dumps(corps).encode() if corps else None, headers=entetes)
    try:
        with urllib.request.urlopen(req, timeout=15) as rep:
            texte = rep.read().decode()
            return rep.status, (json.loads(texte) if texte.startswith(("{", "[")) else texte)
    except urllib.error.HTTPError as e:
        return e.code, None


def verifier(libelle, condition, detail=""):
    global echecs
    echecs += 0 if condition else 1
    print(("OK   " if condition else "ÉCHEC") + f" {libelle} {detail}", flush=True)


statut, page = appel(FRONT + "/")
verifier("front : page d'accueil servie", statut == 200 and 'id="racine"' in page)
statut, produits = appel(FRONT + "/api/catalogue/produits")
verifier("catalogue via la passerelle", statut == 200 and len(produits) == 8, f"({statut})")
statut, session = appel(FRONT + "/api/identite/connexion",
                        {"email": "morticia@petitemaison.fr", "motDePasse": "Epouvante2026!"})
verifier("connexion d'un membre", statut == 200, f"({statut})")
jeton = session["jeton"] if session else ""
verifier("commande refusée sans jeton", appel(FRONT + "/api/commandes")[0] == 401)

avant = {s: appel(f"{FRONT}/api/{s}/stats")[1]["recues"] for s in ("notifications", "expedition")}
statut, commande = appel(FRONT + "/api/commandes", {"lignes": [{"produitId": 2, "quantite": 1}]}, jeton)
verifier("commande enregistrée", statut == 201, f"({statut}) {commande.get('id') if commande else ''}")
for service in ("notifications", "expedition"):
    recu = False
    for _ in range(40):
        if appel(f"{FRONT}/api/{service}/stats")[1]["recues"] > avant[service]:
            recu = True
            break
        time.sleep(0.5)
    verifier(f"événement « commande payée » reçu par {service} (bus)", recu)

verifier("mes commandes via Kong", appel(KONG + "/api/commandes", jeton=jeton)[0] == 200)

print("\nTest de bout en bout : " + ("OK" if echecs == 0 else f"{echecs} échec(s)"))
sys.exit(1 if echecs else 0)
