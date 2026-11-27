"""Bus d'événements sur Apache Kafka (modèle « journal distribué »).

Topologie :
    topic <run>.commandes      (3 partitions, clé = client_id)
    topic <run>.<service>.dlq  (dead letter par service, alimenté PAR LE CODE du consommateur)
    un groupe de consommateurs par service ; chaque groupe garde sa position (offset)

Un message lu n'est PAS supprimé : il reste dans le journal pendant la durée de rétention,
et n'importe quel nouveau groupe peut le relire depuis le début.
"""

import os
import time

from confluent_kafka import Consumer, KafkaException, Producer, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic

from bus.evenements import decoder, encoder

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")


class BusKafka:
    nom = "Kafka"

    def __init__(self, run_id: str, confirmations: bool = True):
        self.prefixe = run_id
        self.topic = f"{run_id}.commandes"
        self._creer_topics([NewTopic(self.topic, num_partitions=3, replication_factor=1)])
        self.producteur = Producer(
            {
                "bootstrap.servers": BOOTSTRAP,
                # acks=all + idempotence : écriture confirmée, pas de doublon en cas de nouvel essai
                "acks": "all" if confirmations else "1",
                "enable.idempotence": confirmations,
                "linger.ms": 5,
            }
        )

    def _dlq(self, service: str) -> str:
        return f"{self.prefixe}.{service}.dlq"

    @staticmethod
    def _creer_topics(topics: list) -> None:
        admin = AdminClient({"bootstrap.servers": BOOTSTRAP})
        futures = admin.create_topics(topics)
        for f in futures.values():
            try:
                f.result(timeout=15)
            except KafkaException as exc:
                if "TOPIC_ALREADY_EXISTS" not in str(exc):
                    raise

    def declarer_service(self, service: str) -> None:
        self._creer_topics([NewTopic(self._dlq(service), num_partitions=1, replication_factor=1)])
        # Le groupe de consommateurs naît à sa première lecture. On enregistre tout de suite sa position
        # à la fin actuelle du journal : il recevra les événements FUTURS, comme une file RabbitMQ neuve.
        c = self._consommateur(service, depart="latest")
        positions = []
        for p in range(3):
            _bas, haut = c.get_watermark_offsets(TopicPartition(self.topic, p), timeout=10)
            positions.append(TopicPartition(self.topic, p, haut))
        c.commit(offsets=positions, asynchronous=False)
        c.close()

    def _consommateur(self, service: str, depart: str = "earliest") -> Consumer:
        return Consumer(
            {
                "bootstrap.servers": BOOTSTRAP,
                "group.id": f"{self.prefixe}.{service}",
                "auto.offset.reset": depart,
                "enable.auto.commit": False,
            }
        )

    def publier(self, evts: list[dict]) -> None:
        for evt in evts:
            self.producteur.produce(self.topic, key=evt["client_id"], value=encoder(evt))
            self.producteur.poll(0)
        restants = self.producteur.flush(30)
        if restants:
            raise RuntimeError(f"{restants} message(s) non confirmé(s) par Kafka")

    def consommer(self, service, traiter, max_messages=None, inactivite_s=2.0) -> int:
        c = self._consommateur(service)
        c.subscribe([self.topic])
        ok = lus = 0
        dernier = time.time()
        attente_assignation = time.time() + 15
        try:
            while True:
                msg = c.poll(0.5)
                if msg is None:
                    # On n'arrête pas tant que le groupe n'a pas reçu ses partitions (rééquilibrage)
                    if c.assignment() and time.time() - dernier > inactivite_s:
                        break
                    if not c.assignment() and time.time() > attente_assignation:
                        break
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                dernier = time.time()
                lus += 1
                evt = decoder(msg.value())
                if traiter(evt):
                    ok += 1
                else:
                    # Pas de DLQ native côté consommateur : c'est au code de republier le message
                    self._creer_topics([NewTopic(self._dlq(service), num_partitions=1, replication_factor=1)])
                    self.producteur.produce(self._dlq(service), key=msg.key(), value=msg.value())
                    self.producteur.flush(10)
                if lus % 500 == 0:  # position validée par lot, comme les acquittements RabbitMQ
                    c.commit(asynchronous=False)
                if max_messages and lus >= max_messages:
                    break
        finally:
            if lus % 500:
                c.commit(asynchronous=False)
            c.close()
        return ok

    def taille_dlq(self, service: str) -> int:
        c = Consumer({"bootstrap.servers": BOOTSTRAP, "group.id": f"{self.prefixe}.inspection"})
        _bas, haut = c.get_watermark_offsets(TopicPartition(self._dlq(service), 0), timeout=10)
        c.close()
        return haut

    def fermer(self) -> None:
        self.producteur.flush(10)
