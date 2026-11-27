# Documentation du projet

**La Petite Maison de l'Épouvante** veut lancer `petitemaisonepouvante.com` : vente en ligne, fanzine numérique avec liseuse, espace communautaire de troc avec chat, recommandations et notifications. Cette documentation présente la démarche de développement que nous proposons, de l'analyse du besoin à la soutenance.

Chaque document correspond à une **story** du board Jira (US-xx.x) et sert au moins un **critère de la grille d'évaluation**. Les sources qui font foi sont le sujet et la grille, dans [sujet](sujet/).

---

## Par où commencer

| Vous voulez… | Lisez |
|---|---|
| Comprendre le besoin en 5 minutes | [Synthèse du besoin](cadrage/synthese-du-besoin.md) |
| Voir la solution proposée dans son ensemble | [Recommandation globale](soutenance/recommandation-globale.md) |
| Préparer ou suivre la soutenance | [Déroulé de la soutenance](soutenance/deroule-de-la-soutenance.md) |
| Lancer les démonstrations | [README du dépôt](../README.md) (boutique de démonstration, pipelines, Kubernetes) |

---

## Plan de la documentation

| Dossier | Contenu | Documents |
|---|---|---|
| [sujet](sujet/) | Sujet du projet, contexte de l'entreprise, grille d'évaluation | [Consignes](sujet/consignes.pdf) · [Contexte](sujet/contexte-petite-maison-epouvante.pdf) · [Grille](sujet/grille-evaluation.xlsx) |
| [cadrage](cadrage/) | Ce que veut l'entreprise, qui fait quoi dans l'équipe, comment on suit l'avancement | [Synthèse du besoin](cadrage/synthese-du-besoin.md) · [Rôles et tâches](cadrage/roles-et-taches.md) · [Suivi du projet](cadrage/suivi-du-projet.md) |
| [qualite-devsecops](qualite-devsecops/) | Exigences de qualité, cycle de vie DevSecOps, métiers | [Attributs de qualité](qualite-devsecops/attributs-de-qualite.md) · [Cycle DevSecOps](qualite-devsecops/cycle-devsecops.md) · [Métiers et interactions](qualite-devsecops/metiers-et-interactions.md) |
| [architecture](architecture/) | Découpage en composants et architecture physique, sans nommer les technologies | [Composants fonctionnels](architecture/composants-fonctionnels.md) · [Architecture macroscopique](architecture/architecture-macroscopique.md) · [Couverture du besoin](architecture/couverture-du-besoin.md) |
| [cicd](cicd/) | **Comparaison CI/CD** : GitHub Actions et Jenkins + Argo CD (GitOps), chaîne dev → accp → prod | [Candidats et critères](cicd/candidats-et-criteres.md) · [Démo GitHub Actions](cicd/demo-github-actions.md) · [Démo Jenkins + Argo CD](cicd/demo-jenkins-argocd.md) · [Comparaison et choix](cicd/comparaison-et-choix.md) · [Branches et environnements](cicd/branches-et-environnements.md) |
| [bus-evenements](bus-evenements/) | **Solution technique n°1** : bus d'événements, RabbitMQ et Kafka | [Domaine et critères](bus-evenements/domaine-et-criteres.md) · [Démo RabbitMQ](bus-evenements/demo-rabbitmq.md) · [Démo Kafka](bus-evenements/demo-kafka.md) · [Comparaison et choix](bus-evenements/comparaison-et-choix.md) |
| [passerelle-api](passerelle-api/) | **Solution technique n°2** : passerelle d'API, Spring Cloud Gateway et Kong | [Spring Cloud Gateway ou Kong](passerelle-api/spring-cloud-gateway-ou-kong.md) |
| [kubernetes-et-tests](kubernetes-et-tests/) | Environnement managé (intérieur de Kubernetes) et stratégie de tests | [Architecture Kubernetes](kubernetes-et-tests/architecture-kubernetes.md) · [Catégories de tests](kubernetes-et-tests/categories-de-tests.md) · [Tests dans le pipeline](kubernetes-et-tests/tests-dans-le-pipeline.md) |
| [securite](securite/) | Politique de sécurité et amélioration continue | [Inventaire du parc](securite/inventaire-du-parc.md) · [Contrôles et scans](securite/controles-et-scans.md) · [Supervision et incidents](securite/supervision-et-incidents.md) · [Amélioration continue](securite/amelioration-continue.md) |
| [soutenance](soutenance/) | Synthèse, déroulé minuté, organisation du groupe, préparation des questions | [Recommandation globale](soutenance/recommandation-globale.md) · [Déroulé de la soutenance](soutenance/deroule-de-la-soutenance.md) · [Organisation et bilan](soutenance/organisation-et-bilan.md) · [Répétitions et questions](soutenance/repetitions-et-questions.md) |

Les dossiers se lisent dans l'ordre du tableau. En bas de chaque document, des liens mènent au document précédent, au sommaire et au suivant.

---

## Correspondance avec la grille d'évaluation

| Critère de la grille | Points | Documents |
|---|---|---|
| 2 plateformes CI/CD expérimentées, démo des avantages et inconvénients | 2 | [cicd](cicd/) |
| 2 solutions techniques expérimentées, démo des avantages et inconvénients | 3 | [bus-evenements](bus-evenements/) et [passerelle-api](passerelle-api/) |
| Architecture physique : composants, services, interactions avec BDD et messagerie | 3 | [architecture](architecture/) |
| Schéma du cycle de vie DevSecOps, toutes les phases expliquées | 2 | [Cycle DevSecOps](qualite-devsecops/cycle-devsecops.md) |
| Métiers nécessaires et leurs interactions | 1 | [Métiers et interactions](qualite-devsecops/metiers-et-interactions.md) |
| Architecture interne de l'environnement managé | 2 | [Architecture Kubernetes](kubernetes-et-tests/architecture-kubernetes.md) |
| Attributs qualité cohérents avec le contexte | 1 | [Attributs de qualité](qualite-devsecops/attributs-de-qualite.md) |
| Types de tests positionnés dans le pipeline, liés aux exigences qualité | 2 | [Catégories de tests](kubernetes-et-tests/categories-de-tests.md) · [Tests dans le pipeline](kubernetes-et-tests/tests-dans-le-pipeline.md) |
| Politique de sécurité et amélioration continue | 2 | [securite](securite/) |
| Organisation du groupe, bilan (points forts, axes d'amélioration) | 1 | [Rôles et tâches](cadrage/roles-et-taches.md) · [Organisation et bilan](soutenance/organisation-et-bilan.md) |
| Présentation fluide et professionnelle | 1 | [Déroulé de la soutenance](soutenance/deroule-de-la-soutenance.md) · [Répétitions et questions](soutenance/repetitions-et-questions.md) |

---

## Identifiants utilisés dans les documents

| Identifiant | Signification | Défini dans |
|---|---|---|
| **US-xx.x** | Story du board Jira (EPIC xx) | [Rôles et tâches](cadrage/roles-et-taches.md) |
| **F-xx** | Fonctionnalité demandée par l'entreprise | [Synthèse du besoin](cadrage/synthese-du-besoin.md) |
| **C-xx** | Contrainte (hébergement en Europe, RGAA, sécurité…) | [Synthèse du besoin](cadrage/synthese-du-besoin.md) |
| **UI-x** | Interfaces : site client, back-office | [Composants fonctionnels](architecture/composants-fonctionnels.md) |
| **EN-x** | Entrée et sécurité : protection périphérique, passerelle, identité | [Composants fonctionnels](architecture/composants-fonctionnels.md) |
| **SV-x** | Services de vente et logistique : catalogue, commandes, paiement, stocks, expédition, abonnements | [Composants fonctionnels](architecture/composants-fonctionnels.md) |
| **SC-x** | Services de contenus : liseuse, contenus éditoriaux | [Composants fonctionnels](architecture/composants-fonctionnels.md) |
| **SM-x** | Services communautaires : annonces, chat, modération | [Composants fonctionnels](architecture/composants-fonctionnels.md) |
| **SP-x** | Services de personnalisation et d'engagement : comptes, recommandations, notifications | [Composants fonctionnels](architecture/composants-fonctionnels.md) |
| **TR-x** | Services transverses : bus d'événements, médias, observabilité, secrets | [Composants fonctionnels](architecture/composants-fonctionnels.md) |
| **Membre A à D** | Les 4 membres du groupe | [Rôles et tâches](cadrage/roles-et-taches.md) |

---

## Conventions de rédaction

- **Un document = une story.** L'en-tête de chaque document donne la story, le lien Jira, le responsable, son binôme relecteur et les documents d'entrée.
- **Schémas faits maison**, en Mermaid dans le Markdown (rendu direct sur GitHub et dans VS Code).
- **Chaque choix est justifié par le contexte** de l'entreprise, et chaque comparaison donne les forces, faiblesses et limites des deux solutions avant de conclure.
- **Les chiffres viennent de mesures réelles** sur la boutique de démonstration, avec la date et le script qui permet de les reproduire.
