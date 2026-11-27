# Boutique de démonstration — La Petite Maison de l'Épouvante

Application **front + microservices** qui sert de support **unique** à toutes les démonstrations de la soutenance : les deux solutions CI/CD, les deux comparaisons techniques (bus d'événements, passerelle d'API) et l'orchestrateur Kubernetes. Elle reprend les composants de l'architecture [US-03.2](../../docs/architecture/US-03.2_architecture_macroscopique.md).

```
                         Navigateur ── http://localhost:3000
                              │
                    ┌─────────┴─────────┐
                    │ front (React) │ NGINX non-root, notifications en direct (SSE)
                    └─────────┬─────────┘
             ┌────────────────┴────────────────┐
   EN-2 Spring Cloud Gateway :8080 Kong 3.9 :8000 ← comparaison n°2 (US-05.5)
   (JWT, limitation par membre, (JWT, limitation par
    coupe-circuit, Redis) application, délais)
             └────────────────┬────────────────┘
   ┌──────────┬───────────────┼───────────────┬──────────────┐
 identité catalogue commandes notifications expédition (Spring Boot 4, Java 21)
 EN-3 JWT SV-1 (PG) SV-2 (PG) SP-3 (SSE) SV-5
                              │ publie « commande payée » ▲ ▲
                              ▼ │ │
                  TR-1 Bus d'événements : RabbitMQ | Kafka ← comparaison n°1 (US-05.1 à 05.4)
                              (même code : Spring Cloud Stream, broker choisi au démarrage)
```

| Dossier | Contenu |
|---|---|
| `front/` | React 18 + Vite, tests Vitest, image NGINX non-root |
| `backend/` | Maven multi-modules : `contrats` (événements versionnés), `identite`, `catalogue`, `commandes`, `notifications`, `expedition`, `passerelle` |
| `kong/`, `postgres/` | Images Kong (configuration déclarative intégrée) et PostgreSQL (une base par service) |
| `docker-compose.yml`, `boutique.py` | Lancement local et bascule du bus et de la passerelle |
| `scenarios/` | Scénarios automatisés des comparaisons et mesures |
| `.github/workflows/ci.yml`, `Jenkinsfile`, `jenkins/`, `ci/`, `demo/` | Les deux pipelines CI/CD, leurs scripts communs, les scénarios « pipeline rouge » |
| `k8s/` | Déploiement de la boutique sur Kubernetes (3 zones, cloisonnement réseau) |
| `.trivyignore.yaml` | Registre des vulnérabilités acceptées (justifiées et datées) |

## Prérequis

- Docker Desktop démarré (8 Go de mémoire conseillés)
- Python 3.11 ou plus récent (bibliothèque standard uniquement)
- Pour Kubernetes : `minikube` et `kubectl`

## 1. Lancer la boutique (environ 1 min, plus le premier build)

```bash
cd demos/boutique
python boutique.py demarrer # RabbitMQ + passerelle Spring par défaut
```

Ouvrir **http://localhost:3000**, se connecter (`morticia@petitemaison.fr` / `Epouvante2026!`), commander : la notification « commande payée » arrive **en direct** dans le panneau de droite. L'en-tête affiche la passerelle et le bus utilisés.

```bash
python boutique.py bus kafka # bascule du bus (environ 30 s, aucune image reconstruite)
python boutique.py passerelle kong # le front passe par Kong (recharger la page)
python boutique.py etat
python boutique.py arreter # --effacer pour supprimer aussi les données
```

| Console | URL |
|---|---|
| RabbitMQ | http://localhost:15672 (`demo` / `demo`) |
| Kafka (kafka-ui) | http://localhost:8081 |
| Kong Manager | http://localhost:8002 |

## 2. Comparaison n°1 : bus d'événements, RabbitMQ et Kafka

```bash
python boutique.py bus rabbit && python scenarios/bus.py --pause
python boutique.py bus kafka && python scenarios/bus.py --pause
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
python scenarios/passerelle.py spring --pause
python scenarios/passerelle.py kong --pause
```

| Étape | Spring Cloud Gateway | Kong 3.9 |
|---|---|---|
| Routage, jetons absents, falsifiés ou expirés → 401 | OK | (messages plus explicites) |
| Rafale d'un membre → 429 | OK | |
| Un **autre membre** juste après la rafale | 5/5 | 0/5 (quota par application) |
| Panne du service commandes | 503 JSON en ~1 s | 504 texte brut en ~2 s |

```bash
python scenarios/mesures.py # latence ajoutée, mémoire, démarrage, délai commande → notification
```

## 4. CI/CD : GitHub Actions et Jenkins, de dev à la production

Les deux pipelines enchaînent **les mêmes étapes avec les mêmes outils et les mêmes scripts** (`ci/`). Ils tournent directement sur le dépôt du projet : workflow [`.github/workflows/boutique.yml`](../../.github/workflows/boutique.yml) et [`Jenkinsfile`](Jenkinsfile). La stratégie complète est décrite dans [US-04.5](../../docs/cicd/US-04.5_branches_environnements.md).

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
sh k8s/demo.sh preparer                       # cluster minikube (une fois)
cd jenkins
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
sh demo/scenario.sh regression     # TVA passée à 21 % : les tests du catalogue échouent
sh demo/scenario.sh secret         # clé d'API de paiement commitée : gitleaks bloque
git commit -am "scénario de démo" && git push
sh demo/scenario.sh reset && git commit -am "retour au vert" && git push
```

> Sur GitHub, la *push protection* peut refuser le secret avant même le pipeline : une couche de défense supplémentaire, à montrer comme telle.

## 5. Kubernetes : la boutique dans 3 zones, en recette et en production

```bash
sh k8s/demo.sh preparer            # la veille : cluster minikube à 2 nœuds + chargement des images
sh k8s/demo.sh composants          # control plane, etcd, scheduler, kubelet, kube-proxy visibles
sh k8s/demo.sh deployer            # production : prod-publique, prod-applicative, prod-donnees (ENV=accp pour la recette)
sh k8s/demo.sh ouvrir              # boutique servie par Kubernetes : http://localhost:3001
sh k8s/demo.sh auto-reparation     # une instance du catalogue supprimée est recréée
sh k8s/demo.sh mise-a-jour         # 4 instances puis redémarrage progressif sans coupure
sh k8s/demo.sh cloisonnement       # contourner la passerelle, atteindre la base, ou passer de la recette à la production : bloqué
sh k8s/demo.sh nettoyer
```

## 6. Plan de secours

| Aléa | Solution |
|---|---|
| Pas d'Internet | Tout est local sauf GitHub Actions : montrer la **vidéo** d'un run GitHub, et Jenkins en direct (images téléchargées la veille) |
| Machine lente | Lancer `boutique.py demarrer` avant la soutenance. Kubernetes : seulement `composants` et `auto-reparation` |
| Une démo plante | Vidéo de secours de cette démo, sans chercher à corriger en direct (15 s maximum) |
| Port déjà utilisé | `python boutique.py arreter` puis relancer. Jenkins utilise le port 8090, Kubernetes le port 3001 |

## Constats faits en construisant la boutique

Ils nourrissent les comparaisons et la politique de sécurité :

- **Coupe-circuit trop court** (1 s par défaut) : la passerelle Spring a renvoyé 503 alors que la commande était enregistrée (premier envoi vers Kafka plus lent). Risque de double commande. Délai porté à 5 s.
- **Coupe-circuit trop long à se refermer** (60 s par défaut) : réglé à 10 s.
- **Cache DNS des passerelles** : après la recréation des conteneurs, **Kong a envoyé `/api/commandes` vers un autre service** pendant 56 s (ancienne IP réattribuée), et Spring a renvoyé des 500. Corrigé des deux côtés par un cache DNS court. Sur Kubernetes, l'IP stable des Services évite ce problème.
- **Vulnérabilités** : Spring Boot 3.4 portait des failles critiques corrigées seulement dans Spring Framework 7. Le scan des images a bloqué le pipeline et imposé la migration vers **Spring Boot 4.0**. Une faille non exploitable de l'image PostgreSQL est acceptée, avec justification et date d'expiration (`.trivyignore.yaml`).
