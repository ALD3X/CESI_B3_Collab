"""Bus d'événements sur RabbitMQ (modèle « file de messages »).

Topologie :
    exchange topic  <run>.evenements  --(commande.#)-->  file <run>.<service>  (une file par service)
    exchange direct <run>.dlx         --(<service>)--->  file <run>.<service>.dlq

Un message acquitté est SUPPRIMÉ de la file : il n'y a pas d'historique rejouable.
"""

import os

import pika

from bus.evenements import decoder, encoder

HOTE = os.environ.get("RABBITMQ_HOST", "localhost")


class BusRabbitMQ:
    nom = "RabbitMQ"

    def __init__(self, run_id: str, confirmations: bool = True, lot: int = 500):
        self.prefixe = run_id
        self.exchange = f"{run_id}.evenements"
        self.dlx = f"{run_id}.dlx"
        params = pika.ConnectionParameters(
            host=HOTE, port=5672, credentials=pika.PlainCredentials("demo", "demo"), heartbeat=60
        )
        self.cnx = pika.BlockingConnection(params)
        self.ch = self.cnx.channel()
        # Garantie d'écriture, équivalente à acks=all côté Kafka :
        #   lot > 1  : transaction AMQP validée tous les `lot` messages (confirmation par lot, comme Kafka)
        #   lot == 1 : « publisher confirm » synchrone, le client attend chaque message (le plus lent)
        self.lot = lot if confirmations else 0
        if self.lot == 1:
            self.ch.confirm_delivery()
        elif self.lot > 1:
            self.ch.tx_select()
        self.ch.exchange_declare(self.exchange, exchange_type="topic", durable=True)
        self.ch.exchange_declare(self.dlx, exchange_type="direct", durable=True)

    def _file(self, service: str) -> str:
        return f"{self.prefixe}.{service}"

    def declarer_service(self, service: str) -> None:
        file, dlq = self._file(service), f"{self._file(service)}.dlq"
        self.ch.queue_declare(dlq, durable=True)
        self.ch.queue_bind(dlq, self.dlx, routing_key=service)
        self.ch.queue_declare(
            file,
            durable=True,
            arguments={"x-dead-letter-exchange": self.dlx, "x-dead-letter-routing-key": service},
        )
        self.ch.queue_bind(file, self.exchange, routing_key="commande.#")

    def publier(self, evts: list[dict]) -> None:
        props = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent, content_type="application/json")
        for i, evt in enumerate(evts, 1):
            self.ch.basic_publish(self.exchange, routing_key=evt["type"], body=encoder(evt), properties=props)
            if self.lot > 1 and i % self.lot == 0:
                self.ch.tx_commit()
        if self.lot > 1:
            self.ch.tx_commit()

    def consommer(self, service, traiter, max_messages=None, inactivite_s=2.0) -> int:
        """Retourne le nombre de messages traités avec succès."""
        # Canal de lecture dédié (le canal de publication peut être transactionnel)
        ch = self.cnx.channel()
        ch.basic_qos(prefetch_count=500)
        ok = 0
        lus = 0
        for methode, _props, corps in ch.consume(self._file(service), inactivity_timeout=inactivite_s):
            if methode is None:  # plus rien depuis `inactivite_s`
                break
            lus += 1
            if traiter(decoder(corps)):
                ch.basic_ack(methode.delivery_tag)
                ok += 1
            else:
                # Rejet sans remise en file : RabbitMQ route NATIVEMENT le message vers la DLQ
                ch.basic_nack(methode.delivery_tag, requeue=False)
            if max_messages and lus >= max_messages:
                break
        ch.cancel()
        ch.close()
        return ok

    def taille_dlq(self, service: str) -> int:
        return self.ch.queue_declare(f"{self._file(service)}.dlq", passive=True).method.message_count

    def fermer(self) -> None:
        if self.cnx.is_open:
            self.cnx.close()
