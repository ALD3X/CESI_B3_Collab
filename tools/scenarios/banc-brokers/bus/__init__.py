"""Deux implémentations du même bus d'événements (TR-1) : RabbitMQ et Kafka.

Les deux classes exposent la même interface, pour que le scénario et le banc
de mesure soient strictement identiques :

    declarer_service(service)          -> prépare la réception pour un service abonné
    publier(evts)                      -> publie une liste d'événements de façon durable
    consommer(service, traiter, ...)   -> lit les événements du service ; traiter(evt) -> bool
    taille_dlq(service)                -> nombre de messages rejetés (dead letter)
    fermer()
"""


def creer_bus(nom: str, run_id: str, **options):
    if nom == "rabbitmq":
        from bus.bus_rabbitmq import BusRabbitMQ

        return BusRabbitMQ(run_id, **options)
    if nom == "kafka":
        from bus.bus_kafka import BusKafka

        return BusKafka(run_id, **options)
    raise ValueError(f"Broker inconnu : {nom} (attendu : rabbitmq ou kafka)")
