# Démo EPIC 05 : bus d'événements, RabbitMQ et Apache Kafka

Deux implémentations du **même composant d'architecture**, TR-1 « Bus d'événements » ([US-03.2](../../docs/architecture/US-03.2_architecture_macroscopique.md)), soumises au **même scénario** et au **même banc de mesure**.

```
docker-compose.yml   RabbitMQ (+ console) · Kafka en mode KRaft (+ console kafka-ui)
bus/evenements.py    Événement métier « commande payée » et règle de validation
bus/bus_rabbitmq.py  Bus sur RabbitMQ : exchange topic → une file par service → DLQ native
bus/bus_kafka.py     Bus sur Kafka : topic à 3 partitions → un groupe de consommateurs par service
scenario.py          Scénario de démonstration identique (4 étapes, 7 vérifications automatiques)
bench.py             Banc de mesure de débit identique
Dockerfile.bench     Client de mesure exécuté dans le réseau Docker (mesure équitable)
```

## Prérequis

- Docker Desktop démarré
- Python 3.11 ou plus récent

```bash
cd demos/messaging
docker compose up -d --wait            # environ 20 s si les images sont déjà téléchargées
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt      # Linux/macOS : .venv/bin/python
```

| Console | URL | Identifiants |
|---|---|---|
| RabbitMQ | http://localhost:15672 | `demo` / `demo` |
| Kafka (kafka-ui) | http://localhost:8081 | aucun |

## 1. Scénario de démonstration (environ 20 s par broker)

```bash
.venv/Scripts/python scenario.py rabbitmq --pause     # --pause : attendre Entrée entre les étapes
.venv/Scripts/python scenario.py kafka --pause
```

| Étape | Ce qu'on montre | RabbitMQ | Kafka |
|---|---|---|---|
| 1. Diffusion | 5 « commandes payées » reçues par **chaque** service abonné (notifications, expédition) | ✅ 5 / 5 | ✅ 5 / 5 |
| 2. Panne | Le service expédition est arrêté pendant 5 commandes, puis redémarre | ✅ rattrape les 5 | ✅ rattrape les 5 |
| 3. Rejeu | Un **nouveau** service (recommandation) veut l'historique des commandes | **0** : les messages consommés sont supprimés | **10** : le journal est relu depuis le début |
| 4. Poison | Un événement invalide (montant négatif) est isolé dans une file de rebut | ✅ DLQ **native** (1 argument de file) | ✅ DLQ **écrite dans notre code** |

Pendant le scénario, ouvrir la console de chaque broker pour montrer les files (RabbitMQ) ou les topics, les partitions et les positions des groupes (Kafka).

## 2. Banc de mesure

Le client tourne **dans le réseau Docker**. Depuis l'hôte Windows, le proxy de ports de Docker Desktop ajoute environ 50 ms à chaque aller-retour synchrone, ce qui fausserait la comparaison.

```bash
docker build -t pm-bench -f Dockerfile.bench .
docker run --rm --network petite-maison-messaging_default pm-bench bench.py rabbitmq --n 20000
docker run --rm --network petite-maison-messaging_default pm-bench bench.py kafka --n 20000
docker run --rm --network petite-maison-messaging_default pm-bench bench.py rabbitmq --n 2000 --confirmation-unitaire
docker stats --no-stream
```

Les résultats sont analysés dans [US-05.4](../../docs/technologies/US-05.4_choix_technique.md).

## 3. Plan de secours

| Aléa | Solution |
|---|---|
| Images non téléchargées / pas d'Internet | Faire `docker compose pull` la veille. La démo est ensuite **100 % locale** |
| Kafka lent à démarrer | Lancer `docker compose up -d --wait` **avant** la soutenance |
| Un broker en échec | Capture vidéo du scénario (1 min par broker) enregistrée la veille |

Arrêt : `docker compose down` (ajouter `-v` pour effacer les données).
