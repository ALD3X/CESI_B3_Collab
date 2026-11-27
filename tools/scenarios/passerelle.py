"""Scénario IDENTIQUE pour les deux passerelles d'API (US-05.5), joué sur la boutique.

    python tools/scenarios/passerelle.py spring [--pause]
    python tools/scenarios/passerelle.py kong   [--pause]

Les deux passerelles tournent en même temps devant les mêmes services (Spring :8080, Kong :8000).
  1. Routage   : chaque chemin atteint le bon service
  2. Sécurité  : /api/commandes refuse les jetons absents, falsifiés ou expirés
  3. Rafale    : un membre qui envoie 30 requêtes d'un coup est limité (429), sans pénaliser les autres
  4. Panne     : le service commandes tombe → réponse propre et rapide, catalogue intact, rétablissement
"""

from __future__ import annotations

import argparse
import sys
import time

from outils import Verifications, compose, connexion, etape, http, jeton_forge

CIBLES = {"spring": 8080, "kong": 8000}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cible", choices=list(CIBLES))
    parser.add_argument("--pause", action="store_true", help="attendre Entrée entre les étapes")
    args = parser.parse_args()
    port = CIBLES[args.cible]
    v = Verifications()
    print(f"Passerelle testée : {args.cible} (http://localhost:{port})")

    etape("1. Routage", args.pause)
    statut, corps, _ = http("GET", "/api/catalogue/produits/1", port)
    v.verifier("catalogue, sans jeton", statut == 200 and "prix_ttc" in corps, f"{statut} {str(corps)[:60]}")
    statut, corps, _ = http("POST", "/api/identite/connexion", port,
                            corps={"email": "morticia@petitemaison.fr", "motDePasse": "Epouvante2026!"})
    v.verifier("connexion → jeton émis par le service identité", statut == 200, f"{statut}")
    jeton = corps["jeton"]
    statut, corps, _ = http("GET", "/api/commandes", port, jeton)
    v.verifier("mes commandes, avec jeton", statut == 200, f"{statut}, {len(corps)} commandes")

    etape("2. Sécurité : jetons refusés", args.pause)
    for libelle, j in [("sans jeton", None),
                       ("jeton signé avec un autre secret", jeton_forge(secret="secret-de-l-attaquant-qui-ne-colle-pas-42")),
                       ("jeton expiré", jeton_forge(expire_dans=-60))]:
        statut, corps, _ = http("GET", "/api/commandes", port, j)
        v.verifier(f"{libelle} → 401", statut == 401, f"{statut} {str(corps or '')[:50]}")

    etape("3. Rafale : 30 requêtes d'un coup par le même membre", args.pause)
    voisin = connexion("vincent", port)
    time.sleep(1.1)   # repartir d'une fenêtre de limitation vide
    codes = [http("GET", "/api/commandes", port, jeton)[0] for _ in range(30)]
    acceptees, limitees = codes.count(200), codes.count(429)
    print("   " + "".join("█" if c == 200 else "░" if c == 429 else "?" for c in codes) + "   █ 200   ░ 429")
    v.verifier("la passerelle limite le débit (des 429 apparaissent)", limitees > 0,
               f"{acceptees} acceptées, {limitees} limitées")
    codes_voisin = [http("GET", "/api/commandes", port, voisin)[0] for _ in range(5)]
    v.verifier("un autre membre n'est pas pénalisé par la rafale", codes_voisin.count(200) == 5,
               f"membre voisin : {codes_voisin.count(200)}/5 acceptées")

    etape("4. Panne du service commandes", args.pause)
    time.sleep(1.1)
    compose("stop", "commandes")
    print("   ⛔ service commandes arrêté")
    try:
        statut, corps, duree = http("GET", "/api/commandes", port, jeton, delai=90)
        v.verifier("erreur 5xx renvoyée au client (pas de blocage)", 500 <= statut < 600, f"{statut} en {duree:.2f} s")
        v.verifier("réponse rapide (moins de 3 s)", duree < 3)
        print(f"   ↳ corps de la réponse : {str(corps)[:100]}")
        v.verifier("le catalogue reste disponible (panne isolée)", http("GET", "/api/catalogue/produits/1", port)[0] == 200)
    finally:
        debut = time.perf_counter()
        compose("start", "commandes")
    statut = 0
    while time.perf_counter() - debut < 120 and statut != 200:
        time.sleep(0.5)
        try:
            statut = http("GET", "/api/commandes", port, jeton, delai=5)[0]
        except OSError:
            statut = 0
    v.verifier("rétablissement automatique après redémarrage", statut == 200,
               f"commandes de nouveau servies {time.perf_counter() - debut:.0f} s après le redémarrage")

    return v.bilan(args.cible)


if __name__ == "__main__":
    sys.exit(main())
