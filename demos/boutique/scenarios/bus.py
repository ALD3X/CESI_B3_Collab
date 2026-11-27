"""Scénario IDENTIQUE pour les deux bus d'événements (US-05.2 / US-05.3), joué sur la boutique.

    python boutique.py bus rabbit   puis   python scenarios/bus.py [--pause]
    python boutique.py bus kafka    puis   python scenarios/bus.py [--pause]

Cas d'usage : l'événement « commande payée » publié par le service commandes (US-03.2 §3.1).
  1. Diffusion : 5 commandes passées dans la boutique → reçues par CHAQUE service abonné
  2. Panne     : le service expédition est arrêté pendant 5 commandes, puis redémarre → aucune perte
  3. Rejeu     : un NOUVEAU service (recommandations) arrive et veut l'historique des commandes
  4. Poison    : un événement invalide (montant négatif) est rejeté et isolé en file de rebut (DLQ)

Le code des services est le même pour les deux bus (Spring Cloud Stream) : seul le broker change.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request

from outils import (Verifications, attendre, commander, compose, connexion, docker, etape, etat, http, stats)

ATTENDU_REJEU = {"rabbit": "0 (seulement les messages futurs)", "kafka": "tout l'historique"}


def taille_dlq(bus: str, groupe: str) -> int:
    if bus == "rabbit":
        req = urllib.request.Request(f"http://localhost:15672/api/queues/%2F/commandes.{groupe}.dlq")
        req.add_header("Authorization", "Basic ZGVtbzpkZW1v")   # demo:demo (console locale)
        try:
            with urllib.request.urlopen(req, timeout=5) as rep:
                return json.loads(rep.read())["messages"]
        except urllib.error.HTTPError:
            return 0
    sortie = docker("exec", "boutique-kafka-1", "/opt/kafka/bin/kafka-get-offsets.sh",
                    "--bootstrap-server", "localhost:9092", "--topic", f"error.commandes.{groupe}")
    return sum(int(ligne.split(":")[-1]) for ligne in sortie.splitlines() if ligne.count(":") == 2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pause", action="store_true", help="attendre Entrée entre les étapes (démo en direct)")
    args = parser.parse_args()

    bus = etat()["bus"]
    v = Verifications()
    t0 = time.perf_counter()
    print(f"Bus d'événements : {'RabbitMQ' if bus == 'rabbit' else 'Kafka'} (boutique sur http://localhost:3000)")
    jeton = connexion("morticia")

    etape("1. Diffusion : 5 commandes passées dans la boutique", args.pause)
    n0, e0 = stats("notifications")["recues"], stats("expedition")["recues"]
    codes = [commander(jeton, produit=i) for i in range(1, 6)]
    print(f"   commandes enregistrées : {codes.count(201)}/5")
    n = attendre(lambda: stats("notifications")["recues"] - n0 >= 5 and stats("notifications")["recues"] - n0) or 0
    e = attendre(lambda: stats("expedition")["recues"] - e0 >= 5 and stats("expedition")["recues"] - e0) or 0
    v.verifier("notifications reçues", n == 5, f"{n} (attendu 5)")
    v.verifier("expéditions reçues", e == 5, f"{e} (attendu 5)")

    etape("2. Panne du service expédition pendant 5 nouvelles commandes", args.pause)
    compose("stop", "expedition")
    print("   ⛔ service expédition arrêté")
    n0 = stats("notifications")["recues"]
    codes = [commander(jeton, produit=i) for i in range(1, 6)]
    print(f"   commandes enregistrées pendant la panne : {codes.count(201)}/5")
    n = attendre(lambda: stats("notifications")["recues"] - n0 >= 5 and stats("notifications")["recues"] - n0) or 0
    v.verifier("notifications reçues (service en ligne)", n == 5, f"{n} (attendu 5)")
    print("   … le service expédition redémarre (nouveau processus, compteur remis à zéro) …")
    compose("up", "-d", "--wait", "expedition")
    e = attendre(lambda: (stats("expedition") or {}).get("recues", 0) >= 5 and stats("expedition")["recues"], 30) or 0
    v.verifier("expéditions rattrapées après redémarrage", e == 5, f"{e} (attendu 5)")

    etape("3. Nouveau service « recommandations » : relire l'historique des commandes", args.pause)
    groupe = f"recommandations-{int(time.time()) % 100000}"
    compose("up", "-d", "--wait", "recommandations", profils=("rejeu",), env={"GROUPE_REJEU": groupe})
    time.sleep(6)   # laisser le temps de relire ce qui existe
    relues = http("GET", "/api/recommandations/stats", 8096)[1]["recues"]
    compose("rm", "-sf", "recommandations", profils=("rejeu",))
    if bus == "rabbit":
        v.verifier("commandes passées relues par le nouveau service", relues == 0,
                   f"{relues} : une file créée maintenant ne reçoit que les messages futurs")
    else:
        v.verifier("commandes passées relues par le nouveau service", relues >= 10,
                   f"{relues} : tout l'historique conservé par le topic, depuis le début")

    etape("4. Événement poison (montant négatif)", args.pause)
    dlq0, n0 = taille_dlq(bus, "notifications"), stats("notifications")["recues"]
    statut = http("POST", "/api/commandes/demo/evenement-invalide", jeton=jeton)[0]
    print(f"   événement invalide publié ({statut})")
    dlq = attendre(lambda: taille_dlq(bus, "notifications") - dlq0 >= 1 and taille_dlq(bus, "notifications") - dlq0, 15) or 0
    v.verifier("messages traités", stats("notifications")["recues"] - n0 == 0, "0 (attendu 0)")
    v.verifier("message isolé en DLQ (service notifications)", dlq == 1, f"{dlq} (attendu 1) après 3 tentatives")

    print(f"\nDurée totale : {time.perf_counter() - t0:.0f} s")
    return v.bilan("RabbitMQ" if bus == "rabbit" else "Kafka")


if __name__ == "__main__":
    sys.exit(main())
