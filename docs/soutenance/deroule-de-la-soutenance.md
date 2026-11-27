# Déroulé de la soutenance et scénarios des démos

> **Story :** US-08.2 · **Jira :** [SCRUM-39](https://maalsi25.atlassian.net/browse/SCRUM-39) · **Epic :** EPIC 08, Synthèse, soutenance et retour d'expérience
> **Responsable :** Membre A, avec les 4 orateurs · **Binôme :** Membre C
> **Démos :** toutes jouées sur la [boutique de démonstration](../../README.md) (front React + microservices Spring Boot) : pipelines, scénarios du bus et des passerelles, Kubernetes

**But :** un déroulé **minuté et stable** de la soutenance (20 min), avec **10 min de démonstrations**, une répartition claire de la parole (une personne pour la vision d'ensemble, une par comparaison) et une solution de repli pour chaque démo.

---

## 1. Qui présente quoi

| Membre | Rôle dans la soutenance | Temps de parole | Démos |
|---|---|---|---|
| **A** | **Vision d'ensemble** : besoin, qualité, architecture, DevSecOps, Kubernetes, tests, sécurité, recommandation et bilan | 7:30 | Kubernetes |
| **B** | **Comparaison CI/CD** : GitHub Actions et Jenkins + Argo CD, chaîne dev → accp → prod | 5:00 | GitHub Actions, Jenkins + Argo CD |
| **C** | **Solution technique n°1** : bus d'événements, RabbitMQ et Kafka | 4:00 | RabbitMQ, Kafka |
| **D** | **Solution technique n°2** : passerelle d'API, Spring Cloud Gateway et Kong | 3:00 | Spring Cloud Gateway et Kong |

A ouvre et ferme la soutenance : le jury suit un fil rouge unique, et chaque comparaison est portée par la personne qui l'a menée de bout en bout. **Chaque membre présente au moins une démo.**

---

## 2. Déroulé minuté (20 min)

| Début | Durée | Qui | Séquence | Type | Critère de la grille |
|---|---|---|---|---|---|
| 00:00 | 1:00 | A | Introduction, contexte, **organisation du groupe**, fil rouge (la boutique de démonstration) | Slides | Organisation |
| 01:00 | 0:45 | A | **Attributs de qualité** | Slide | Attributs qualité |
| 01:45 | 1:00 | A | **Architecture** physique (composants, BDD, messagerie) | Schéma | Architecture |
| 02:45 | 1:00 | A | **Cycle DevSecOps** et **métiers** | Schémas | DevSecOps, métiers |
| 03:45 | 0:30 | B | CI/CD : candidats et critères | Slide | CI/CD |
| 04:15 | **2:00** | B | **Démo GitHub Actions** : de dev à la production | Démo | CI/CD |
| 06:15 | **2:00** | B | **Démo Jenkins + Argo CD** : pipeline rouge, déploiement GitOps, correction d'écart | Démo | CI/CD, tests, sécurité |
| 08:15 | 0:30 | B | Verdict CI/CD | Slide | CI/CD |
| 08:45 | 0:30 | C | Bus d'événements : rôle dans l'architecture, critères | Slide | Solutions techniques |
| 09:15 | **1:30** | C | **Démo RabbitMQ** | Démo | Solutions techniques |
| 10:45 | **1:30** | C | **Démo Kafka** | Démo | Solutions techniques |
| 12:15 | 0:30 | C | Verdict : RabbitMQ en V1 | Slide | Solutions techniques |
| 12:45 | 0:30 | D | Passerelle d'API : rôle dans l'architecture, critères | Slide | Solutions techniques |
| 13:15 | **2:00** | D | **Démo Spring Cloud Gateway et Kong** | Démo | Solutions techniques, sécurité |
| 15:15 | 0:30 | D | Verdict : Spring Cloud Gateway en V1 | Slide | Solutions techniques |
| 15:45 | 0:30 | A | Schéma de l'**orchestrateur** | Schéma | Environnement managé |
| 16:15 | **1:15** | A | **Démo Kubernetes** | Démo | Environnement managé |
| 17:30 | 0:30 | A | **Tests** dans le pipeline | Schéma | Tests |
| 18:00 | 0:45 | A | **Politique de sécurité** | Schéma | Sécurité |
| 18:45 | 0:45 | A + tous | Recommandation globale, **bilan** : points forts, axes d'amélioration (une phrase par membre) | Slide | Organisation, bilan |
| 19:30 | 0:30 | — | *Marge* | — | — |

**Temps de démonstration : 10 min 15 s sur 20** (4 min CI/CD, 3 min bus d'événements, 2 min passerelle, 1 min 15 s Kubernetes).

---

## 3. Ce que dit chacun

### A : vision d'ensemble

| Séquence | Message oral |
|---|---|
| Introduction | « La Petite Maison de l'Épouvante veut vendre en ligne, publier un fanzine numérique et ouvrir un espace de troc entre passionnés, hébergé en Europe, avec une sécurité forte. Nous sommes quatre : un pilote et un relecteur par chantier, un board Jira, une branche Git par story. Tout ce que vous allez voir tourne sur une même application de démonstration, une boutique en microservices rangée dans un monorepo. » |
| Qualité | « Sept exigences priorisées. La sécurité et la fiabilité passent en premier : paiement, données personnelles, pics de vente pendant les festivals. Chacune est vérifiée par un test du pipeline. » |
| Architecture | « Trois zones : publique, applicative, données. Une passerelle unique en entrée, des services par domaine, une base par service, et un bus d'événements entre eux. Deux de ces briques, le bus et la passerelle, sont celles que nous avons comparées. » |
| DevSecOps et métiers | « La sécurité intervient à chaque phase, de la planification à la supervision. » Puis les métiers : qui transmet quoi à qui, et les recrutements à prévoir. |
| Orchestrateur | « Le control plane décide : API server, etcd, scheduler, controller manager. Chaque nœud exécute : kubelet et kube-proxy. » |
| Tests | « Chaque test à l'étape où il est le plus utile : unitaires et couverture sur chaque commit, scans, test de bout en bout avant publication, recette en accp, test de fumée en production. » |
| Sécurité | « Quatre briques : inventaire du parc, scans, supervision, gestion des incidents. Chaque exception est justifiée et datée, et chaque incident devient une règle. » |
| Recommandation et bilan | « GitHub Actions sous conditions, RabbitMQ et Spring Cloud Gateway en V1, Kubernetes managé hébergé en Europe. » Puis chaque membre donne un point fort ou un axe d'amélioration. |

### B : comparaison CI/CD

| Séquence | Message oral |
|---|---|
| Critères | « Deux philosophies, à deux niveaux. Pour la CI : un service intégré à la forge, GitHub Actions, contre un serveur que l'on héberge, Jenkins. Pour le déploiement : un pipeline qui pousse dans le cluster, contre Argo CD, qui tire l'état décrit dans Git depuis l'intérieur du cluster. Même scénario, mêmes scripts des deux côtés. » |
| Verdict | « GitHub Actions gagne sur la CI : rien à maintenir, pour une petite équipe. Argo CD gagne sur le déploiement : la CI ne détient plus les accès à la production, et tout écart avec Git est corrigé. Notre choix : GitHub Actions pour la CI, Argo CD pour le déploiement dès que le cluster européen est en place. » |

### C : bus d'événements

| Séquence | Message oral |
|---|---|
| Critères | « Le bus transporte les événements métier, comme "commande payée", entre les services. Critères fixés avant les démos : fiabilité, relecture de l'historique pour les recommandations, simplicité d'exploitation. » |
| Verdict | « RabbitMQ en V1 : plus simple et 2 à 6 fois plus léger. Kafka si la V2 exige de relire l'historique à grande échelle. Le passage est préparé : le code des services ne change pas. » |

### D : passerelle d'API

| Séquence | Message oral |
|---|---|
| Critères | « La passerelle est la porte d'entrée unique : elle vérifie le jeton, limite le débit et route vers les services. Critères : sécurité des accès, résilience, prise en main par une équipe Spring, effort, empreinte, exploitation, pérennité de la licence. » |
| Verdict | « 63 contre 51 sur 75 : Spring Cloud Gateway pour la V1, avec une règle, aucun réglage par défaut sans test de panne. Kong deviendrait le bon choix si nous ouvrons des API à des partenaires. » |

---

## 4. Scénario détaillé de chaque démo

### Démo 1 : GitHub Actions (B, 2:00)

| Temps | Action à l'écran | Message oral |
|---|---|---|
| 0:00 | `.github/workflows/` dans le dépôt | « Le pipeline est du code, découpé en un fichier par étape. Sur dev, uniquement de l'intégration continue : rien n'est publié ni déployé. La publication et le déploiement continu commencent en recette, sur accp. » |
| 0:20 | Onglet *Actions* : run `dev` vert **lancé avant la soutenance** | « 4 contrôles en parallèle, puis les 9 images : build, scan, test de bout en bout. Sur dev, rien n'est publié. » |
| 0:50 | Run `accp` | « En recette, les images sont publiées une seule fois sur le registre GitHub, et le cluster les tire lui-même. La production reprendra ces mêmes images, sans reconstruction : elle exécutera exactement ce qui a été testé. » |
| 1:20 | Onglet *Environments*, run `prod` | « Seule une version recettée peut partir en production, et uniquement par le workflow de mise en production, réservé aux approbateurs. » |
| 1:45 | — | « Recette et production n'acceptent que des pull requests, imposées par GitHub, et la mise en production attend l'approbation d'un relecteur. Limite : sur un dépôt privé, ces protections exigent l'offre payante. » |

### Démo 2 : Jenkins + Argo CD (B, 2:00)

| Temps | Action à l'écran | Message oral |
|---|---|---|
| 0:00 | http://localhost:8090, job multi-branches **créé par le code** | « Le même pipeline, sur notre propre serveur, hébergeable en Europe. Jenkins fait l'intégration continue, et ne touche jamais au cluster. » |
| 0:20 | **En direct :** `npm run scenario:pipeline-rouge -- secret`, puis commit sur `dev` | « Un développeur commite la clé d'API du prestataire de paiement… » |
| 0:40 | gitleaks rouge, publication sautée | « …la livraison est bloquée. C'est la quality gate de sécurité. » |
| 0:55 | Interface Argo CD (`npm run argocd:ouvrir`), application `boutique-accp` | « Le déploiement, c'est Argo CD, dans le cluster. Il compare en permanence le cluster à Git : voici la recette, synchronisée, avec sa version. » |
| 1:15 | **En direct :** `kubectl -n accp-applicative delete deployment catalogue` | « Quelqu'un supprime un service à la main… Argo CD détecte l'écart avec Git et le recrée tout seul. » |
| 1:45 | Build `prod` arrêté sur l'étape **Approbation** | « En production, Jenkins attend un humain, puis Argo CD synchronise. Le prix à payer : deux outils à exploiter. » |

### Démo 3 : RabbitMQ (C, 1:30)

| Temps | Action à l'écran | Message oral |
|---|---|---|
| 0:00 | **La boutique** (http://localhost:3000) : une commande, la notification arrive en direct | « La commande payée part vers les notifications et l'expédition. » |
| 0:15 | `npm run scenario:bus`, étapes 1 et 2 | « L'expédition tombe en panne pendant 5 commandes… elle redémarre et rattrape tout : aucune perte. » |
| 0:45 | Étape 3 : **0** | « Un nouveau service ne peut pas relire le passé : ce qui est consommé est supprimé. » |
| 1:05 | Étape 4 et file `commandes.notifications.dlq` | « Le message invalide est isolé par le broker lui-même. » |

### Démo 4 : Kafka (C, 1:30)

| Temps | Action à l'écran | Message oral |
|---|---|---|
| 0:00 | `npm run boutique -- bus kafka` (fait avant), puis `npm run scenario:bus` | « Même boutique, même code des services, autre broker : la bascule prend 30 secondes. » |
| 0:20 | kafka-ui, onglet *Consumers* | « Kafka mémorise la position de chaque service dans un journal. » |
| 0:40 | Étape 3 : **tout l'historique** | « Différence clé : un nouveau service, comme les recommandations de la V2, relit tout l'historique. » |
| 1:00 | Étape 4, puis `docker stats` | « La file de rebut est fournie par le framework. Et Kafka consomme 2 à 6 fois plus de mémoire. » |

### Démo 5 : Spring Cloud Gateway et Kong (D, 2:00)

| Temps | Action à l'écran | Message oral |
|---|---|---|
| 0:00 | La boutique, puis `npm run boutique -- passerelle kong` et rechargement : l'en-tête affiche « Kong » | « Les deux passerelles tournent en même temps devant les mêmes services. Pour le client, rien ne change. » |
| 0:20 | `npm run scenario:passerelle -- spring --pause`, étape 3 | « Un membre envoie une rafale de 30 requêtes : il est limité. Un autre membre juste après : 5 sur 5, la limite est par membre. » |
| 0:50 | `npm run scenario:passerelle -- kong --pause`, étape 3 | « Même rafale avec Kong : l'autre membre est bloqué, 0 sur 5. Le quota est partagé par toute l'application : pendant une vente flash, un robot bloquerait tous les clients. » |
| 1:20 | Étape 4 (service commandes arrêté) | « Panne d'un service : Spring répond en 1 seconde avec un message lisible par le front. Kong, avec ses réglages par défaut, faisait attendre 75 secondes. » |
| 1:40 | Tableau des mesures | « Kong a ses atouts : 53 lignes de configuration contre 195, un seul conteneur, une latence quasi nulle. » |

### Démo 6 : Kubernetes (A, 1:15)

| Temps | Action à l'écran | Message oral |
|---|---|---|
| 0:00 | `kubectl get pods -A -o wide` (déjà déployé) | « La boutique en production : 3 zones, 2 nœuds, et la recette à côté, dans ses propres zones. » |
| 0:15 | `npm run k8s -- auto-reparation` | « Je supprime une instance du catalogue : le controller manager la recrée, l'autre instance sert le trafic entre-temps. » |
| 0:50 | `npm run k8s -- cloisonnement` | « Contourner la passerelle, atteindre la base, ou passer de la recette à la production : bloqué. » |

---

## 5. Questions du jury : qui répond en premier

| Thème | Répond en premier |
|---|---|
| Besoin, architecture, Kubernetes, tests, sécurité, organisation | A |
| CI/CD, chaîne de livraison, DevSecOps | B |
| Bus d'événements, RabbitMQ, Kafka | C |
| Passerelle d'API, contrôle des accès, limitation du débit | D |

Les autres complètent si besoin. Chacun doit pouvoir défendre l'ensemble des choix : voir [Répétitions et questions](repetitions-et-questions.md).

---

## 6. Préparation technique

### La veille (J-1)

- [ ] `npm run boutique:demarrer`, puis `npm run boutique -- bus kafka` et retour à `rabbit` : toutes les images sont en cache, démo **sans Internet**.
- [ ] Un **run vert** sur GitHub Actions **et** sur Jenkins + Argo CD (`npm run jenkins:demarrer`, `npm run jenkins:connecter`, `npm run argocd:installer`).
- [ ] `npm run k8s -- preparer` puis `deployer` (environ 8 min).
- [ ] Lancer `tools/scenarios/bus.py` sur les deux bus et `tools/scenarios/passerelle.py` sur les deux passerelles : **7/7, 7/7, 12/12 et 11/12** attendus.
- [ ] Enregistrer une **vidéo de secours** de 1 à 2 min par démo (6 vidéos), copiées sur 2 ordinateurs et une clé USB.
- [ ] Vérifier la **taille de police** du terminal (≥ 18 pt) et le **mode sombre/clair** lisible au vidéoprojecteur.

### Une heure avant (H-1)

- [ ] Démarrer Docker Desktop, puis `npm run boutique:demarrer -- --bus rabbit --sans-build` et Jenkins (`npm run jenkins:demarrer`).
- [ ] `minikube start -p boutique` (le cluster garde les déploiements de la veille).
- [ ] **20 min avant :** lancer un build de la branche `prod` dans Jenkins (*Build Now*) : il doit attendre l'approbation pendant la démo de B (la demande expire au bout de 30 min).
- [ ] Remettre la boutique sur la passerelle Spring (`npm run boutique -- passerelle spring`) avant la démo de D.
- [ ] Ouvrir les onglets dans l'ordre de passage : GitHub Actions, Jenkins (:8090), Argo CD (:8443, `npm run argocd:ouvrir`), boutique (:3000), console RabbitMQ (:15672), kafka-ui (:8081). Ouvrir 4 terminaux nommés (CI, BUS, PASSERELLE, K8S).
- [ ] Passer une commande dans la boutique **une fois à blanc** (la notification doit s'afficher).
- [ ] Désactiver les notifications et la mise en veille de l'ordinateur.

### Solutions de repli

| Aléa | Repli | Qui décide |
|---|---|---|
| Pas d'Internet | GitHub Actions en **vidéo**. Tout le reste est **100 % local** | Démonstrateur |
| Une démo plante | **Vidéo de secours** de la démo, sans chercher à corriger en direct (≤ 15 s de tentative) | Démonstrateur |
| Retard de plus d'1 min à 08:45 | Démo Kafka réduite aux étapes 3 et 4 (1 min) | Maître du temps |
| Retard de plus d'1 min à 12:45 | Démo des passerelles réduite à l'étape 3 (la limite par membre) | Maître du temps |
| Retard de plus d'1 min à 15:45 | Démo Kubernetes réduite à `auto-reparation` | Maître du temps |
| Ordinateur principal en panne | Second ordinateur préparé à l'identique, ou vidéos | A |

**Maître du temps :** Membre D (Membre C pendant la partie de D), avec des repères discrets à 03:45, 08:45, 12:45 et 15:45. A présente plus de la moitié du temps : il ne peut pas surveiller la montre en même temps.

---

[← Recommandation globale consolidée](recommandation-globale.md) · [Sommaire](../README.md) · [Organisation du groupe et retour d'expérience →](organisation-et-bilan.md)
