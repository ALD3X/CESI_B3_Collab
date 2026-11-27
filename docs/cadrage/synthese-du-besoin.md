# Synthèse du besoin de l'entreprise

> **Story :** US-01.1 · **Jira :** [SCRUM-14](https://maalsi25.atlassian.net/browse/SCRUM-14) · **Epic :** EPIC 01, Cadrage et organisation du groupe
> **Source :** `docs/sujet/contexte-petite-maison-epouvante.pdf` (V1, 06/03/2025)
> **Objectif :** identifier les fonctionnalités et les contraintes de la future plateforme `petitemaisonepouvante.com` pour pouvoir justifier ensuite les choix de conception (attributs qualité, architecture, technologies, sécurité).

---

## 1. Contexte de l'entreprise

| Élément | Situation actuelle |
|---|---|
| **Activité historique** | Fanzine horreur, fantastique et heroic fantasy, en version papier et numérique, 4 numéros par an sur abonnement |
| **Commerce physique** | 4 magasins (Angoulême, Aix-en-Provence, Lyon, Londres « The Little House of Thrill ») qui vendent goodies, DVD/Blu-ray, BD et jeux de société |
| **Événementiel** | *Petit Festival de l'Épouvante*, annuel depuis 5 ans : projections, ventes, masterclasses, tournois |
| **Production et édition** | Collectif **Evil Ed** financé par crowdfunding : web série *L'Orc* et la BD associée, 2 séries en pré-production, restauration d'un film italien en Blu-ray. Evil Ed a son propre site vitrine |
| **Présence web** | Site vitrine sur un CMS, sans vente en ligne. Il permet seulement l'abonnement au fanzine et l'inscription à la newsletter |
| **Équipe IT** | Nouvelle équipe : 1 architecte logiciel (ex-lead dev) et 2 développeurs juniors en alternance. D'autres recrutements sont possibles |

### État du SI existant

- **Hétérogène et fragmenté.** Il est géré par un seul technicien, avec l'aide ponctuelle de deux fondateurs venus de l'IT.
- **Applications métiers** (gestion de stock, gestion des fournisseurs, CRM) hébergées chez un **fournisseur cloud français**.
- **Échanges de données manuels** par fichiers CSV. Il n'y a aucune intégration automatisée.
- **Poste de travail :** LibreOffice, messagerie Gmail, postes sous Ubuntu, 1 station Mac pour la PAO (fanzine et newsletters).
- **Magasins :** chaque magasin a son propre système de caisse et **son propre stock**. Les magasins se transfèrent des articles en cas de rupture. Le transporteur est La Poste.
- **Infrastructure :** serveur de fichiers Ubuntu dans un magasin (« Paris »), sauvegardes Veeam, accès par VPN.
- **Evil Ed :** infrastructure média locale à Paris (stations de montage et d'authoring, serveur multimédia redondé sur 2 nœuds).

> **Incohérence à noter :** le contexte parle d'un « magasin de Paris » (serveur de fichiers, station Mac), alors que les magasins listés sont Angoulême, Aix, Lyon et Londres. **Hypothèse retenue :** il s'agit du siège ou des bureaux parisiens, pas d'un point de vente.

---

## 2. Fonctionnalités du périmètre initial (V1)

### 2.1 Vente en ligne (e-commerce)

| ID | Fonctionnalité | Détail |
|---|---|---|
| F-01 | **Catalogue et vente de produits** | Produits également vendus en magasin : figurines, jeux, Blu-ray, BD, goodies |
| F-02 | **Exclusivités web** | Gamme de figurines Evil Ed vendue uniquement sur le site |
| F-03 | **Vente de numéros numériques du fanzine** | À l'unité |
| F-04 | **Liseuse intégrée** | Lecture des numéros achetés dans l'espace de l'utilisateur authentifié |
| F-05 | **Abonnement au fanzine** | Souscription ou renouvellement, en version papier et/ou numérique |
| F-06 | **Paiement en ligne** | *Implicite* : nécessaire pour toute la partie vente |

### 2.2 Recommandations et notifications

| ID | Fonctionnalité | Détail |
|---|---|---|
| F-07 | **Recommandation de produits** | Basée sur les recherches et les achats de l'utilisateur |
| F-08 | **Notifications d'intérêt** | Alerte automatique quand un article lié aux centres d'intérêt est proposé (troc ou vente) |
| F-09 | **Notifications comportementales** *(souhaité, « idéalement »)* | Notifications déclenchées par le comportement de navigation |
| F-10 | **Paramétrage par l'utilisateur** | Réglage des notifications et des recommandations depuis l'espace personnel |

### 2.3 Espace communautaire

| ID | Fonctionnalité | Détail |
|---|---|---|
| F-11 | **Troc et don entre particuliers** | Publier une liste de goodies à échanger ou à donner |
| F-12 | **Liste de recherche** | Lister les articles recherchés (ce qui alimente F-08) |
| F-13 | **Chat entre passionnés** | Messagerie entre utilisateurs |
| F-14 | **Modération** | Modération des annonces, du chat et des utilisateurs (signalement, suppression, bannissement) |

### 2.4 Espace utilisateur

| ID | Fonctionnalité | Détail |
|---|---|---|
| F-15 | **Compte et authentification** | Inscription, connexion, gestion du profil |
| F-16 | **Suivi des commandes** | Statut et suivi de livraison (La Poste) |
| F-17 | **Historique des achats** | Commandes passées, factures, numéros du fanzine achetés |

### 2.5 Contenus publics

| ID | Fonctionnalité | Détail |
|---|---|---|
| F-18 | **News et articles de fond** | Accessibles à tous les internautes, sans authentification |
| F-19 | **Back-office éditorial** | *Implicite* : publication des contenus par l'équipe |

### 2.6 Fonctionnalités implicites ou back-office

Ces fonctionnalités ne figurent pas explicitement dans le sujet mais sont nécessaires au fonctionnement du périmètre V1 :

- **Back-office de gestion :** catalogue, prix, commandes, utilisateurs, modération.
- **Synchronisation des stocks** avec le stock **par magasin** et la logistique (préparation, expédition La Poste).
- **Intégration au SI existant** (stock, fournisseurs, CRM) pour remplacer les échanges CSV manuels.
- **Newsletter** : reprise de la fonctionnalité du site actuel.

---

## 3. Contraintes

### 3.1 Contraintes explicites (issues du sujet)

| ID | Contrainte | Source dans le sujet | Impact sur la conception |
|---|---|---|---|
| C-01 | **Accessibilité RGAA** | « respecter la RGAA » | Conformité de l'interface, audits d'accessibilité dans le pipeline de tests |
| C-02 | **Ergonomie et fluidité** | « interface fluide, ergonomique » | Performance côté client, temps de réponse, responsive design |
| C-03 | **Sécurité forte** | « contrainte forte, plateforme à visée commerciale » | Paiement, données personnelles, authentification robuste, démarche DevSecOps |
| C-04 | **Hébergement en Europe** | « aimerait que l'application soit hébergée en Europe » | Choix du cloud et souveraineté des données. Le fournisseur cloud français actuel est un candidat naturel |
| C-05 | **SI hétérogène et fragmenté** | « Système d'information » entre guillemets, échanges CSV | Besoin d'une couche d'intégration (API, bus de messages), interopérabilité |
| C-06 | **Stock géré par magasin** | « chaque magasin a son propre stock » | Disponibilité en ligne calculée sur plusieurs stocks, transferts entre magasins, cohérence des données |

### 3.2 Contraintes déduites du contexte

| ID | Contrainte | Justification |
|---|---|---|
| C-07 | **Conformité RGPD** | Données personnelles, profilage pour les recommandations et notifications comportementales (consentement nécessaire), hébergement UE |
| C-08 | **Conformité paiement (PCI-DSS)** | Vente en ligne. À déléguer de préférence à un prestataire de paiement |
| C-09 | **Multi-pays, multi-devises** | Magasin à Londres : clientèle britannique, livraison au Royaume-Uni (hors UE), GBP, version anglaise du site |
| C-10 | **Pics de charge** | Festival annuel, sortie des numéros du fanzine, lancement d'exclusivités Evil Ed : il faut de la scalabilité |
| C-11 | **Équipe IT réduite et junior** | 1 architecte et 2 alternants : privilégier des technologies maîtrisables, des services managés et une forte automatisation (CI/CD) |
| C-12 | **Protection des contenus numériques** | Fanzine lisible dans la liseuse uniquement : contrôle d'accès et limitation du téléchargement libre |
| C-13 | **Contenus générés par les utilisateurs** | Troc et chat impliquent une obligation de modération et de traitement des signalements (responsabilité de l'hébergeur) |
| C-14 | **Évolutivité vers V2/V3** | L'architecture doit pouvoir accueillir les enchères et le streaming sans refonte |

---

## 4. Périmètre : V1 et ambitions futures

| Version | Fonctionnalités | Statut pour le projet |
|---|---|---|
| **V1 (plateforme initiale)** | E-commerce (produits, fanzine numérique, abonnements), liseuse, recommandations, notifications, espace communautaire (troc/don, chat, modération), espace utilisateur (suivi, historique), news et articles publics | **Dans le périmètre** |
| **V2** | Système d'**enchères** de type eBay | Hors périmètre initial. L'architecture doit le permettre |
| **V2** | **Diffusion des productions Evil Ed** (web séries, films) | Hors périmètre initial. Prévoir la capacité de streaming vidéo |
| **V3** *(« peut-être »)* | **Diffusion des films du festival** en mode restreint (places limitées, créneaux horaires fixes) | Hors périmètre initial. Prévoir la billetterie virtuelle et le contrôle des accès simultanés |

> Le sujet précise que *« les nouvelles fonctionnalités sont acceptées pour la mise en œuvre dans le cadre de l'exercice »*. Les éléments V2 et V3 peuvent donc servir à **justifier des choix d'architecture** (découplage, scalabilité, broker de messages), mais ils ne sont **pas** à concevoir en détail.

---

## 5. Points clés pour la suite du projet

Cette synthèse alimente directement les US suivantes :

- **US-02.1, attributs de qualité :** la sécurité (C-03, C-07, C-08), l'accessibilité (C-01), la performance et la scalabilité (C-02, C-10), la maintenabilité (C-11), l'interopérabilité (C-05) et l'évolutivité (C-14) sont les attributs les mieux justifiés par le contexte.
- **US-03.1, composants fonctionnels :** les blocs F-01 à F-19 se regroupent naturellement en domaines : *Catalogue/Vente*, *Contenus et liseuse*, *Communauté*, *Recommandation et notification*, *Identité/Utilisateur*, *Intégration SI*.
- **US-03.3, couverture du besoin :** utiliser les identifiants F-xx et C-xx de ce document comme matrice de traçabilité.
- **EPIC 07, sécurité :** l'inventaire du parc applicatif doit inclure l'existant (CMS, stock, CRM, caisses, serveur de fichiers, infrastructure Evil Ed).

### Questions ouvertes / hypothèses à valider en équipe

1. « Magasin de Paris » : siège ou point de vente ? *(hypothèse : bureaux parisiens)*
2. La plateforme remplace-t-elle le site vitrine CMS actuel ? *(hypothèse : oui)* Le site Evil Ed est-il intégré ? *(hypothèse : non en V1)*
3. La vente en ligne puise-t-elle dans le stock des magasins ou dans un stock web dédié ? *(hypothèse : stocks magasins agrégés et stock dédié aux exclusivités web)*
4. Le site est-il bilingue FR/EN pour Londres ? *(hypothèse : oui)*

---

[Sommaire](../README.md) · [Répartition des rôles et des tâches →](roles-et-taches.md)
