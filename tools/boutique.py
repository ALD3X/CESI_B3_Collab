"""Pilotage de la boutique de démonstration.

  python tools/boutique.py demarrer [--bus rabbit|kafka] [--passerelle spring|kong]
  python tools/boutique.py bus kafka            # bascule du bus d'événements (services redémarrés, même code)
  python tools/boutique.py passerelle kong      # bascule de la passerelle utilisée par le front
  python tools/boutique.py etat
  python tools/boutique.py arreter [--effacer]  # --effacer : supprime aussi les données (PostgreSQL)

Le choix courant est mémorisé dans .etat.json : une bascule ne change que ce qu'on lui demande.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent                                   # racine du monorepo
COMPOSE = ["docker", "compose", "-f", str(RACINE / "infra" / "compose" / "compose.yaml")]
ETAT = ICI / ".etat.json"
BUS = {"rabbit": "RabbitMQ", "kafka": "Kafka"}
PASSERELLES = {
    "spring": ("passerelle-spring:8080", "Spring Cloud Gateway"),
    "kong": ("kong:8000", "Kong"),
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def lire_etat() -> dict:
    try:
        return json.loads(ETAT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"bus": "rabbit", "passerelle": "spring"}


def environnement(etat: dict) -> dict:
    hote, nom = PASSERELLES[etat["passerelle"]]
    return {**os.environ, "BUS": etat["bus"], "BUS_NOM": BUS[etat["bus"]],
            "PASSERELLE_HOTE": hote, "PASSERELLE_NOM": nom}


def compose(etat: dict, *args: str, profils: tuple[str, ...] = ()) -> None:
    commande = list(COMPOSE)
    for p in profils:
        commande += ["--profile", p]
    subprocess.run([*commande, *args], cwd=RACINE, env=environnement(etat), check=True)


def demarrer(etat: dict, construire: bool = True) -> None:
    autre = "kafka" if etat["bus"] == "rabbit" else "rabbit"
    print(f"▶ Bus : {BUS[etat['bus']]} · passerelle du front : {PASSERELLES[etat['passerelle']][1]}")
    # Le broker non utilisé est arrêté pour libérer la mémoire
    compose(etat, "stop", *(["kafka", "kafka-ui"] if autre == "kafka" else ["rabbitmq"]), profils=(autre,))
    compose(etat, "up", "-d", *(["--build"] if construire else []), "--wait", profils=(etat["bus"],))
    ETAT.write_text(json.dumps(etat), encoding="utf-8")
    print("\n✅ Boutique prête : http://localhost:3000")
    print("   Passerelles : Spring http://localhost:8080 · Kong http://localhost:8000 (console :8002)")
    print("   Console du bus : " + ("RabbitMQ http://localhost:15672 (demo/demo)" if etat["bus"] == "rabbit"
                                    else "Kafka http://localhost:8081"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = parser.add_subparsers(dest="action", required=True)
    d = sous.add_parser("demarrer")
    d.add_argument("--bus", choices=list(BUS))
    d.add_argument("--passerelle", choices=list(PASSERELLES))
    d.add_argument("--sans-build", action="store_true", help="ne pas reconstruire les images")
    sous.add_parser("bus").add_argument("choix", choices=list(BUS))
    sous.add_parser("passerelle").add_argument("choix", choices=list(PASSERELLES))
    sous.add_parser("etat")
    a = sous.add_parser("arreter")
    a.add_argument("--effacer", action="store_true")
    args = parser.parse_args()

    etat = lire_etat()
    if args.action == "demarrer":
        etat["bus"] = args.bus or etat["bus"]
        etat["passerelle"] = args.passerelle or etat["passerelle"]
        demarrer(etat, construire=not args.sans_build)
    elif args.action == "bus":
        etat["bus"] = args.choix
        demarrer(etat, construire=False)
    elif args.action == "passerelle":
        etat["passerelle"] = args.choix
        compose(etat, "up", "-d", "--no-deps", "front", profils=(etat["bus"],))
        ETAT.write_text(json.dumps(etat), encoding="utf-8")
        print(f"✅ Le front passe maintenant par {PASSERELLES[args.choix][1]} (rechargez la page).")
    elif args.action == "etat":
        print(f"Bus : {BUS[etat['bus']]} · passerelle du front : {PASSERELLES[etat['passerelle']][1]}")
        compose(etat, "ps", "--format", "table {{.Name}}\t{{.Status}}", profils=("rabbit", "kafka", "rejeu"))
    elif args.action == "arreter":
        compose(etat, "down", *(["-v"] if args.effacer else []), profils=("rabbit", "kafka", "rejeu"))


if __name__ == "__main__":
    main()
