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

Le dépôt est un **monorepo turbo**. Toutes les commandes passent par les **scripts du [`package.json`](package.json)** (`npm run …`), sur le poste comme dans les deux pipelines.

---

## Prérequis

- Docker Desktop (8 Go de mémoire conseillés)
- Node.js 26 LTS et JDK 25 LTS
- Python 3.11 ou plus récent
- Git (sous Windows, son shell sert à lancer les scripts)
- Pour Kubernetes : `minikube` et `kubectl`

---

## Démarrage rapide

```bash
npm install                  # une fois
npm test                     # tests du front et du backend
npm run boutique:demarrer    # toute la boutique dans Docker
```

Ouvrir **http://localhost:3000** et se connecter avec `morticia@petitemaison.fr` / `Epouvante2026!`.

```bash
npm run boutique:etat        # bus et passerelle utilisés
npm run boutique:arreter     # ajouter « -- --effacer » pour supprimer aussi les données
```

---

## Scripts

| Domaine | Scripts (`npm run …`) |
|---|---|
| **Développement** | `dev` (front en mode développement), `build` |
| **Tests** | `test` (front + backend), `test:front`, `test:back`, `test:e2e` (boutique complète, parcours client) |
| **Sécurité** | `securite` (les trois), `securite:secrets` (gitleaks), `securite:sast` (Semgrep), `securite:sca` (Trivy) |
| **Images** | `images:version`, `images:build`, `images:scan`, `images:publier`, `images:present`, `images:etiqueter` |
| **Déploiement** | `deployer -- accp`, `deployer -- prod` |
| **Boutique locale** | `boutique:demarrer`, `boutique:etat`, `boutique:arreter`, `boutique -- bus kafka`, `boutique -- passerelle kong` |
| **Démos** | `scenario:bus`, `scenario:passerelle -- spring` (ou `kong`), `scenario:mesures`, `scenario:pipeline-rouge -- regression` (ou `secret`, `reset`) |
| **Kubernetes** | `k8s -- preparer`, puis `deployer`, `auto-reparation`, `cloisonnement`, `nettoyer` |
| **Jenkins** | `jenkins:demarrer` (http://localhost:8090, `admin` / `admin`), `jenkins:connecter` (accès au cluster), `jenkins:arreter` |

Consoles : RabbitMQ http://localhost:15672 (`demo` / `demo`) · Kafka http://localhost:8081 · Kong http://localhost:8002

---

## CI/CD

Les deux pipelines font les mêmes étapes, avec les mêmes scripts npm.

| Branche | Ce que fait le pipeline |
|---|---|
| `feature/*`, `dev` | **Intégration continue** : tests, analyse de sécurité, build des images, scan, test de bout en bout |
| `accp` | Idem, puis **publication des images** et **déploiement en recette** (Kubernetes) |
| `prod` | Reprise des images recettées, **approbation**, déploiement en production, retour arrière si échec |

`accp` et `prod` n'acceptent que des **pull requests** : GitHub refuse tout push direct sur ces branches.

```bash
gh pr create --base accp --head dev --fill && gh pr merge --merge    # vers la recette
gh pr create --base prod --head accp --fill && gh pr merge --merge   # vers la production
```

Mettre en production :
- **GitHub Actions** : `gh workflow run mise-en-production.yml --ref prod`, puis approbation dans l'onglet Actions
- **Jenkins** : bouton « Mettre en production » sur le build `prod`

Détails : [branches et environnements](docs/cicd/branches-et-environnements.md).
