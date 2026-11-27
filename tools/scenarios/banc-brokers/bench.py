"""Banc de mesure identique pour les deux brokers (débit publication / consommation).

    python bench.py rabbitmq --n 20000
    python bench.py rabbitmq --n 20000 --sans-confirmation
    python bench.py kafka    --n 20000

Avec confirmations (défaut), par lot : RabbitMQ transaction tous les 500 messages, Kafka acks=all + idempotence.
Option --confirmation-unitaire (RabbitMQ) : le client attend la confirmation de CHAQUE message.
Les deux garantissent qu'un message confirmé est écrit sur disque côté broker.
"""

import argparse
import sys
import time

from bus import creer_bus
from bus.evenements import commande_payee, encoder

sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("broker", choices=["rabbitmq", "kafka"])
    parser.add_argument("--n", type=int, default=20000)
    parser.add_argument("--sans-confirmation", action="store_true")
    parser.add_argument("--confirmation-unitaire", action="store_true", help="RabbitMQ : attendre chaque message")
    args = parser.parse_args()

    run_id = f"bench{int(time.time()) % 100000}"
    options = {"confirmations": not args.sans_confirmation}
    if args.broker == "rabbitmq" and args.confirmation_unitaire:
        options["lot"] = 1
    bus = creer_bus(args.broker, run_id, **options)
    bus.declarer_service("bench")
    evts = [commande_payee(i) for i in range(args.n)]
    taille = len(encoder(evts[0]))

    t = time.perf_counter()
    bus.publier(evts)
    pub = time.perf_counter() - t

    t = time.perf_counter()
    recus = bus.consommer("bench", lambda _e: True, max_messages=args.n, inactivite_s=5)
    con = time.perf_counter() - t
    bus.fermer()

    mode = ("sans confirmation" if args.sans_confirmation
            else "confirmation unitaire" if args.confirmation_unitaire else "confirmation par lot")
    print(f"{bus.nom} ({mode}) · {args.n} messages de ~{taille} octets")
    print(f"  publication  : {pub:6.2f} s  → {args.n / pub:>9,.0f} msg/s".replace(",", " "))
    print(f"  consommation : {con:6.2f} s  → {recus / con:>9,.0f} msg/s ({recus} reçus)".replace(",", " "))
    return 0 if recus == args.n else 1


if __name__ == "__main__":
    sys.exit(main())
