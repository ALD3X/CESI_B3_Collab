# La Petite Maison de l'Épouvante

Projet collaboratif CESI : la démarche de développement de la plateforme `petitemaisonepouvante.com`, et une **boutique de démonstration** (front React + microservices Spring Boot) qui sert de support à toutes les démos de la soutenance.

- **Documentation :** [docs/README.md](docs/README.md)
- **Démos :** deux chaînes CI/CD (GitHub Actions, Jenkins), deux comparaisons techniques (RabbitMQ / Kafka, Spring Cloud Gateway / Kong), Kubernetes

---

## Contenu du dépôt

| Dossier | Contenu |
|---|---|
| [`apps/front`](apps/front) | Front React + Vite |
| [`apps/back`](apps/back) | Microservices Spring Boot : identité, catalogue, commandes, notifications, expédition, passerelle |
| [`infra/`](infra) | Docker Compose, Kubernetes, Jenkins, scripts CI/CD, images Kong et PostgreSQL |
| [`tools/`](tools) | Lancement de la boutique et scénarios de démonstration |
| [`docs/`](docs) | Documentation du projet |
| [`.github/workflows/`](.github/workflows), [`Jenkinsfile`](Jenkinsfile) | Les deux pipelines CI/CD |

Le dépôt est un **monorepo turbo** : `apps/front` et `apps/back` sont des espaces de travail npm, et turbo lance leurs tâches avec un cache.

---

## Prérequis

- Docker Desktop (8 Go de mémoire conseillés)
- Node.js 26 LTS et JDK 25 LTS
- Python 3.11 ou plus récent
- Pour Kubernetes : `minikube` et `kubectl`

Toutes les commandes se lancent **depuis la racine du dépôt**.

---

## Démarrage rapide

```bash
npm install                        # une fois
npx turbo run test                 # tests du front et du backend
python tools/boutique.py demarrer  # toute la boutique dans Docker
```

Ouvrir **http://localhost:3000** et se connecter avec `morticia@petitemaison.fr` / `Epouvante2026!`.

```bash
python tools/boutique.py etat      # bus et passerelle utilisés
python tools/boutique.py arreter   # --effacer pour supprimer aussi les données
```

---

## Démonstrations

| Démo | Commandes |
|---|---|
| **Bus d'événements** : RabbitMQ ou Kafka | `python tools/boutique.py bus rabbit` (ou `kafka`), puis `python tools/scenarios/bus.py --pause` |
| **Passerelle d'API** : Spring Cloud Gateway ou Kong | `python tools/scenarios/passerelle.py spring --pause` (ou `kong`) |
| **Mesures** des deux comparaisons | `python tools/scenarios/mesures.py` |
| **Kubernetes** | `sh infra/k8s/demo.sh preparer`, puis `deployer`, `auto-reparation`, `cloisonnement` |
| **Pipeline rouge** | `sh tools/demo/scenario.sh regression` (ou `secret`), commit, puis `sh tools/demo/scenario.sh reset` |

Consoles : RabbitMQ http://localhost:15672 (`demo` / `demo`) · Kafka http://localhost:8081 · Kong http://localhost:8002

---

## CI/CD

Les deux pipelines font les mêmes étapes, avec les mêmes scripts (`infra/ci/`).

| Branche | Ce que fait le pipeline |
|---|---|
| `feature/*`, `dev` | **Intégration continue** : tests, analyse de sécurité, build des images, scan, test de bout en bout |
| `accp` | Idem, puis **publication des images** et **déploiement en recette** (Kubernetes) |
| `prod` | Reprise des images recettées, **approbation**, déploiement en production, retour arrière si échec |

`accp` et `prod` n'acceptent que des **pull requests** : GitHub refuse tout push direct sur ces branches.

Faire avancer une version :

```bash
gh pr create --base accp --head dev --fill && gh pr merge --merge    # vers la recette
gh pr create --base prod --head accp --fill && gh pr merge --merge   # vers la production
```

Mettre en production :
- **GitHub Actions** : `gh workflow run mise-en-production.yml --ref prod`, puis approbation dans l'onglet Actions
- **Jenkins** : bouton « Mettre en production » sur le build `prod`

Lancer Jenkins en local :

```bash
cd infra/jenkins
docker compose up -d --build   # http://localhost:8090 (admin / admin)
sh connecter-minikube.sh       # accès au cluster Kubernetes local
```

Détails : [branches et environnements](docs/cicd/branches-et-environnements.md).
