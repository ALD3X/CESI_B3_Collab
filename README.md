# La Petite Maison de l'Épouvante — monorepo

Projet collaboratif CESI : documentation du projet et **boutique de démonstration**, une application **front + microservices** qui sert de support **unique** à toutes les démonstrations de la soutenance : les deux solutions CI/CD, les deux comparaisons techniques (bus d'événements, passerelle d'API) et l'orchestrateur Kubernetes.

## Organisation du dépôt (monorepo turbo)

```
.
├── apps/
│   ├── front/          React 18 + Vite, tests Vitest, image NGINX non-root          (@boutique/front)
│   └── back/           Spring Boot 4 / Java 25, Maven multi-modules + Maven Wrapper (@boutique/back)
├── infra/
│   ├── compose/        compose.yaml (boutique complète), dev.yml (environnement dev), ci.yml (tests CI)
│   ├── ci/             scripts communs aux deux pipelines : images, scan, test de bout en bout, déploiement
│   ├── k8s/            base Kustomize + surcouches accp et prod (3 zones, cloisonnement réseau)
│   ├── jenkins/        Jenkins configuré par le code (JCasC, job multi-branches) + registre local
│   └── kong/, postgres/  images Kong (configuration déclarative) et PostgreSQL (une base par service)
├── tools/              boutique.py (lancement, bascule bus/passerelle), scenarios/, resultats/, demo/
├── docs/               documentation du projet : sommaire dans docs/README.md
├── .github/workflows/boutique.yml   Jenkinsfile   turbo.json   package.json
└── .trivyignore.yaml   .gitleaks.toml
```

| Dossier | Contenu |
|---|---|
| `apps/front` | React 18 + Vite, tests Vitest (couverture ≥ 70 %), image NGINX non-root |
| `apps/back` | Maven multi-modules : `contrats` (événements versionnés), `identite`, `catalogue`, `commandes`, `notifications`, `expedition`, `passerelle` |
| `infra/` | Tout ce qui construit, teste et déploie : Docker Compose, scripts CI, Kubernetes, Jenkins, images Kong et PostgreSQL |
| `tools/` | Lancement local, bascule du bus et de la passerelle, scénarios automatisés des comparaisons, scénarios « pipeline rouge » |
| `docs/` | Livrables du projet, rangés dans l'ordre de lecture : [sommaire](docs/README.md), sujet et grille dans [docs/sujet](docs/sujet/) |
| `.github/workflows/boutique.yml`, `Jenkinsfile` | Les deux pipelines CI/CD |
| `.trivyignore.yaml` | Registre des vulnérabilités acceptées (justifiées et datées) |

### Tâches turbo

Les deux applications sont des espaces de travail npm ; turbo orchestre leurs tâches et met leurs résultats en cache (une tâche dont les sources n'ont pas changé n'est pas rejouée).

```bash
npm install                                   # une fois, à la racine
npx turbo run test                            # tests + seuils de couverture du front et du backend, en parallèle
npx turbo run build                           # build Vite + jars Spring Boot
npx turbo run test --filter=@boutique/front   # une seule application
npm run dev                                   # front en mode développement (Vite)
```

Le backend passe par le **Maven Wrapper** (`apps/back/mvnw`) : aucun Maven à installer, même version partout. Toutes les commandes ci-dessous se lancent **depuis la racine du dépôt**.

## Prérequis

- Docker Desktop démarré (8 Go de mémoire conseillés)
- Node.js 26 LTS (turbo, front) et JDK 25 LTS (backend ; Maven est téléchargé par le Maven Wrapper)
- Python 3.11 ou plus récent (bibliothèque standard uniquement)
- Pour Kubernetes : `minikube` et `kubectl`

## 1. Lancer la boutique (environ 1 min, plus le premier build)

```bash
python tools/boutique.py demarrer # RabbitMQ + passerelle Spring par défaut
```

Ouvrir **http://localhost:3000**, se connecter (`morticia@petitemaison.fr` / `Epouvante2026!`), commander : la notification « commande payée » arrive **en direct** dans le panneau de droite. L'en-tête affiche la passerelle et le bus utilisés.

```bash
python tools/boutique.py bus kafka # bascule du bus (environ 30 s, aucune image reconstruite)
python tools/boutique.py passerelle kong # le front passe par Kong (recharger la page)
python tools/boutique.py etat
python tools/boutique.py arreter # --effacer pour supprimer aussi les données
```

| Console | URL |
|---|---|
| RabbitMQ | http://localhost:15672 (`demo` / `demo`) |
| Kafka (kafka-ui) | http://localhost:8081 |
| Kong Manager | http://localhost:8002 |

## 2. Comparaison n°1 : bus d'événements, RabbitMQ et Kafka

```bash
python tools/boutique.py bus rabbit && python tools/scenarios/bus.py --pause
python tools/boutique.py bus kafka && python tools/scenarios/bus.py --pause
```

| Étape (sur la boutique) | RabbitMQ | Kafka |
|---|---|---|
| 1. Diffusion : 5 commandes → notifications **et** expédition | 5 / 5 | 5 / 5 |
| 2. Panne de l'expédition pendant 5 commandes, puis redémarrage | 5 rattrapées | 5 rattrapées |
| 3. Nouveau service « recommandations » : relire l'historique | **0** (messages futurs seulement) | **tout l'historique** |
| 4. Événement poison (montant négatif) → file de rebut après 3 tentatives | DLQ | DLQ (topic `error.*`) |

## 3. Comparaison n°2 : passerelle d'API, Spring Cloud Gateway et Kong

Les deux passerelles tournent en même temps devant les mêmes services.

```bash
python tools/scenarios/passerelle.py spring --pause
python tools/scenarios/passerelle.py kong --pause
```

| Étape | Spring Cloud Gateway | Kong 3.9 |
|---|---|---|
| Routage, jetons absents, falsifiés ou expirés → 401 | OK | (messages plus explicites) |
| Rafale d'un membre → 429 | OK | |
| Un **autre membre** juste après la rafale | 5/5 | 0/5 (quota par application) |
| Panne du service commandes | 503 JSON en ~1 s | 504 texte brut en ~2 s |

```bash
python tools/scenarios/mesures.py # latence ajoutée, mémoire, démarrage, délai commande → notification
```

## 4. CI/CD : GitHub Actions et Jenkins, de dev à la production

Les deux pipelines enchaînent **les mêmes étapes avec les mêmes outils et les mêmes scripts** (`infra/ci/`). Ils tournent directement sur le dépôt du projet : workflow [`.github/workflows/boutique.yml`](.github/workflows/boutique.yml) et [`Jenkinsfile`](Jenkinsfile). La stratégie complète est décrite dans [US-04.5](docs/cicd/branches-et-environnements.md).

```
toutes les branches : secrets ‖ backend (≥ 70 %) ‖ front (≥ 70 %) ‖ SAST + SCA
feature/*  → build des 9 images → scan → test de bout en bout
dev        → idem + publication v-<version> → déploiement dev (Docker Compose, :3100)
accp       → promotion des MÊMES images → déploiement recette (Kubernetes accp-*) → recette validée
prod       → version recettée ? → APPROBATION → déploiement progressif (prod-*) → test de fumée → retour arrière si échec
```

| Branche | Environnement | Accès |
|---|---|---|
| `dev` (par défaut) | Docker Compose, projet `boutique-dev` | http://localhost:3100 |
| `accp` | Kubernetes, namespaces `accp-*` | `kubectl -n accp-publique port-forward svc/front 3002:80` |
| `prod` | Kubernetes, namespaces `prod-*` | `kubectl -n prod-publique port-forward svc/front 3001:80` |

**GitHub Actions** : chaque push sur `dev`, `accp` ou `prod` lance la chaîne de la branche (onglet **Actions**, puis **Environments**). La mise en production se déclenche par **Run workflow** sur la branche `prod`, case « Mettre en production » cochée, par un utilisateur de la variable `APPROBATEURS_PROD`. Sans secret `KUBECONFIG`, les environnements Kubernetes sont créés à la volée dans le runner (cluster kind).

**Jenkins** (100 % local, configuré par le code) :

```bash
sh infra/k8s/demo.sh preparer                       # cluster minikube (une fois)
cd infra/jenkins
docker compose up -d --build                  # http://localhost:8090 (admin / admin), job multi-branches déjà créé
sh connecter-minikube.sh                      # accès de Jenkins au cluster (environnements accp et prod)
```

Le job `petite-maison-boutique` découvre les branches `dev`, `accp`, `prod` et `feature/*` du dépôt toutes les minutes. En production, le build s'arrête sur l'étape **Approbation** : bouton « Mettre en production » (utilisateur `admin`). Images publiées : `curl http://localhost:5000/v2/_catalog`.

**Faire avancer une version :**

```bash
git switch accp && git merge --ff-only dev && git push      # dev → recette
git switch prod && git merge --ff-only accp && git push     # recette → production (puis approbation)
```

**Scénarios « pipeline rouge »** (sur une branche `feature/…` ou sur `dev`) :

```bash
sh tools/demo/scenario.sh regression     # TVA passée à 21 % : les tests du catalogue échouent
sh tools/demo/scenario.sh secret         # clé d'API de paiement commitée : gitleaks bloque
git commit -am "scénario de démo" && git push
sh tools/demo/scenario.sh reset && git commit -am "retour au vert" && git push
```

> Sur GitHub, la *push protection* peut refuser le secret avant même le pipeline : une couche de défense supplémentaire, à montrer comme telle.

## 5. Kubernetes : la boutique dans 3 zones, en recette et en production

```bash
sh infra/k8s/demo.sh preparer            # la veille : cluster minikube à 2 nœuds + chargement des images
sh infra/k8s/demo.sh composants          # control plane, etcd, scheduler, kubelet, kube-proxy visibles
sh infra/k8s/demo.sh deployer            # production : prod-publique, prod-applicative, prod-donnees (ENV=accp pour la recette)
sh infra/k8s/demo.sh ouvrir              # boutique servie par Kubernetes : http://localhost:3001
sh infra/k8s/demo.sh auto-reparation     # une instance du catalogue supprimée est recréée
sh infra/k8s/demo.sh mise-a-jour         # 4 instances puis redémarrage progressif sans coupure
sh infra/k8s/demo.sh cloisonnement       # contourner la passerelle, atteindre la base, ou passer de la recette à la production : bloqué
sh infra/k8s/demo.sh nettoyer
```
