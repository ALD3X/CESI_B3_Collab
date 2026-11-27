"""Événements métier de la démo : « commande payée » (cf. US-03.2, scénario 3.1)."""

import json
import uuid
from datetime import datetime, timezone

TYPE_COMMANDE_PAYEE = "commande.payee"


def commande_payee(numero: int, montant: float | None = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "type": TYPE_COMMANDE_PAYEE,
        "commande": f"CMD-{numero:05d}",
        # La clé client sert au partitionnement Kafka : l'ordre est garanti par client.
        "client_id": f"CLI-{numero % 4}",
        "montant": round(19.90 + numero, 2) if montant is None else montant,
        "horodatage": datetime.now(timezone.utc).isoformat(),
    }


def encoder(evt: dict) -> bytes:
    return json.dumps(evt, ensure_ascii=False).encode("utf-8")


def decoder(brut: bytes) -> dict:
    return json.loads(brut.decode("utf-8"))


def est_valide(evt: dict) -> bool:
    """Règle métier des consommateurs : un montant négatif est un message « poison »."""
    return evt.get("type") == TYPE_COMMANDE_PAYEE and evt.get("montant", -1) >= 0
