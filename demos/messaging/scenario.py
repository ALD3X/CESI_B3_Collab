"""Scénario de démonstration IDENTIQUE pour les deux brokers (US-05.2 / US-05.3).

    python scenario.py rabbitmq
    python scenario.py kafka

Étapes (cas d'usage : événement « commande payée », cf. US-03.2 §3.1) :
  1. Diffusion   : 1 événement publié -> reçu par CHAQUE service abonné (notifications, expédition)
  2. Panne       : le service expédition est arrêté pendant 5 commandes, puis redémarre -> aucune perte
  3. Rejeu       : un NOUVEAU service (recommandation) arrive et veut l'historique des commandes
  4. Poison      : un événement invalide est rejeté et isolé dans une file de rebut (DLQ)
"""

import argparse
import sys
import time

from bus import creer_bus
from bus.evenements import commande_payee, est_valide

sys.stdout.reconfigure(encoding="utf-8")

# Résultats attendus : seule l'étape « rejeu » diffère, c'est la différence de modèle à montrer
ATTENDU = {
    "rabbitmq": {"rejeu": 0},
    "kafka": {"rejeu": 10},
}


def titre(texte: str) -> None:
    print(f"\n━━━ {texte} " + "━" * max(0, 60 - len(texte)))


def verifier(libelle: str, obtenu: int, attendu: int, resultats: list) -> None:
    ok = obtenu == attendu
    resultats.append(ok)
    print(f"  {'✅' if ok else '❌'} {libelle} : {obtenu} (attendu {attendu})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("broker", choices=["rabbitmq", "kafka"])
    parser.add_argument("--pause", action="store_true", help="attendre Entrée entre les étapes (démo en direct)")
    args = parser.parse_args()

    def pause():
        if args.pause:
            input("  [Entrée pour continuer]")

    run_id = f"demo{int(time.time()) % 100000}"
    t0 = time.perf_counter()
    bus = creer_bus(args.broker, run_id)
    resultats: list[bool] = []
    print(f"Broker : {bus.nom} · exécution : {run_id}")

    try:
        titre("0. Abonnement des services notifications et expédition")
        for service in ("notifications", "expedition"):
            bus.declarer_service(service)
        print("  services abonnés aux événements commande.*")
        pause()

        titre("1. Diffusion : 5 commandes payées")
        bus.publier([commande_payee(i) for i in range(1, 6)])
        verifier("notifications reçues", bus.consommer("notifications", est_valide), 5, resultats)
        verifier("expéditions reçues", bus.consommer("expedition", est_valide), 5, resultats)
        pause()

        titre("2. Panne du service expédition pendant 5 nouvelles commandes")
        bus.publier([commande_payee(i) for i in range(6, 11)])
        verifier("notifications reçues (service en ligne)", bus.consommer("notifications", est_valide), 5, resultats)
        print("  … le service expédition redémarre …")
        verifier("expéditions rattrapées après redémarrage", bus.consommer("expedition", est_valide), 5, resultats)
        pause()

        titre("3. Nouveau service « recommandation » : relire l'historique")
        if args.broker == "rabbitmq":
            # Seul moyen avec RabbitMQ : créer une file. Elle ne reçoit que les messages FUTURS.
            bus.declarer_service("recommandation")
        verifier(
            "commandes passées relues par le nouveau service",
            bus.consommer("recommandation", est_valide, inactivite_s=3),
            ATTENDU[args.broker]["rejeu"],
            resultats,
        )
        pause()

        titre("4. Événement poison (montant négatif)")
        bus.publier([commande_payee(99, montant=-5.0)])
        traites = bus.consommer("notifications", est_valide)
        bus.consommer("expedition", est_valide)
        verifier("messages traités", traites, 0, resultats)
        verifier("messages isolés en DLQ (service notifications)", bus.taille_dlq("notifications"), 1, resultats)
    finally:
        bus.fermer()

    duree = time.perf_counter() - t0
    titre(f"Bilan {bus.nom}")
    print(f"  {sum(resultats)}/{len(resultats)} vérifications conformes · durée totale {duree:.1f} s")
    return 0 if all(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
