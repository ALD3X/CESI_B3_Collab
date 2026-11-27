# Attributs de qualité logicielle

> **Story :** US-02.1 · **Jira :** [SCRUM-17](https://maalsi25.atlassian.net/browse/SCRUM-17) · **Epic :** EPIC 02, Qualité logicielle et démarche DevSecOps
> **Responsable :** Membre B · **Binôme :** Membre D
> **Entrée :** [US-01.1, synthèse du besoin](../cadrage/synthese-du-besoin.md) (identifiants F-xx = fonctionnalités, C-xx = contraintes)

**But :** montrer à la direction quelles exigences de qualité sont prioritaires pour `petitemaisonepouvante.com`, pourquoi, et comment on les vérifiera.

**Référentiel :** les définitions reprennent le modèle **ISO/IEC 25010** (qualité du produit logiciel), adapté au vocabulaire du projet.

---

## 1. Synthèse

| Priorité | Attribut | En une phrase | Enjeu principal du cas |
|---|---|---|---|
| 1 (critique) | **Sécurité** | Protéger les données et les transactions contre les accès et usages non autorisés | Paiement en ligne, données personnelles, « contrainte forte » |
| 2 (critique) | **Fiabilité / disponibilité** | Le site fonctionne correctement et reste accessible quand les clients en ont besoin | Plateforme commerciale : une panne fait perdre directement des ventes |
| 3 (structurant) | **Performance** | Le site répond vite, même sous charge | « Interface fluide », conversion e-commerce |
| 4 (structurant) | **Scalabilité** | La plateforme absorbe les pics de charge et la croissance sans refonte | Festival, sortie du fanzine, exclusivités Evil Ed, V2/V3 |
| 5 (structurant) | **Accessibilité** | Le site est utilisable par tous, y compris les personnes en situation de handicap | Exigence RGAA explicite |
| 6 (durable) | **Maintenabilité** | Le code peut être compris, modifié et testé facilement et sans risque | Petite équipe junior, évolutions V2/V3 |
| 7 (durable) | **Interopérabilité** | La plateforme échange des données de façon automatisée avec le SI existant | SI fragmenté, échanges CSV manuels, stock par magasin |

> **Niveaux de priorité :** **critique** = non négociable dès la V1 · **structurant** = structurant pour l'architecture · **durable** = condition de réussite dans la durée

---

## 2. Définition et justification de chaque attribut

### 2.1 Sécurité (critique)

**Définition (ISO 25010) :** capacité du produit à protéger les informations et les données, pour que chaque personne ou système n'y accède qu'au niveau autorisé. Elle couvre 5 sous-caractéristiques :

| Sous-caractéristique | Signification | Application au cas |
|---|---|---|
| **Confidentialité** | Seules les personnes autorisées accèdent aux données | Données clients, adresses, historique d'achats, messages du chat |
| **Intégrité** | Les données ne peuvent pas être modifiées sans autorisation | Prix, commandes, stocks, abonnements |
| **Non-répudiation** | Une action ne peut pas être niée après coup | Commandes et paiements horodatés et tracés |
| **Responsabilité (traçabilité)** | Chaque action peut être attribuée à son auteur | Actions de modération, actions du back-office |
| **Authenticité** | L'identité d'un utilisateur ou d'un système est prouvée | Authentification forte pour l'admin, sessions sécurisées |

**Pourquoi c'est essentiel ici :**
- Le contexte la qualifie de **« contrainte forte »** pour une plateforme à visée commerciale (C-03).
- **Paiement en ligne** (F-06) : la conformité PCI-DSS est obligatoire (C-08).
- **Données personnelles** et **profilage** pour les recommandations et notifications (F-07 à F-09), ce qui implique le RGPD (C-07).
- **Contenus générés par les utilisateurs** (troc, chat : F-11, F-13), avec des risques d'injection, de spam et d'arnaque.
- **Contenus payants** (fanzine numérique, F-03/F-04) à protéger contre l'accès non autorisé (C-12).
- SI existant **peu sécurisé** et géré par une seule personne : la nouvelle plateforme ne doit pas devenir une porte d'entrée.

**Comment on la vérifie :** 0 vulnérabilité critique ou haute ouverte en production, scans automatiques à chaque build (code, dépendances, conteneurs), test d'intrusion avant la mise en production, MFA obligatoire pour les comptes d'administration.

### 2.2 Fiabilité / disponibilité (critique)

**Définition (ISO 25010) :** capacité du système à fournir ses fonctions dans des conditions données, pendant une durée donnée. Elle regroupe :
- **Disponibilité :** le service est opérationnel et accessible quand on en a besoin.
- **Tolérance aux pannes :** le service continue de fonctionner malgré la défaillance d'un composant.
- **Récupérabilité :** après un incident, le service et les données sont rétablis dans un délai et avec une perte maîtrisés.
- **Maturité :** le système fonctionne sans défaillance en usage normal.

**Pourquoi c'est essentiel ici :**
- Chaque minute d'indisponibilité, c'est **du chiffre d'affaires perdu** et une perte de confiance.
- Une commande ou un paiement **ne doit jamais être perdu ou doublé**, même si un composant tombe en panne au milieu d'une transaction.
- Une panne de la recommandation ou du chat **ne doit pas empêcher d'acheter** : il faut isoler les pannes entre composants.
- Le SI actuel a un **point de défaillance unique** (serveur de fichiers dans un seul local). La plateforme ne doit pas reproduire ce schéma.

**Comment on la vérifie :** disponibilité ≥ **99,5 %** par mois (environ 3h40 d'arrêt maximum), RPO ≤ 1 h (perte de données maximale), RTO ≤ 4 h (délai de rétablissement), restauration des sauvegardes testée chaque mois.

### 2.3 Performance (efficacité des performances) (structurant)

**Définition (ISO 25010) :** performance obtenue par rapport aux ressources utilisées. Elle regroupe :
- **Temps de réponse :** délai entre une action de l'utilisateur et le résultat affiché.
- **Utilisation des ressources :** CPU, mémoire et réseau consommés pour rendre le service.
- **Capacité :** volume maximal traité (utilisateurs simultanés, commandes par minute) en respectant les temps de réponse.

**Pourquoi c'est essentiel ici :**
- Le contexte exige une **« interface fluide »** (C-02).
- En e-commerce, chaque seconde de chargement en plus fait baisser le taux de conversion.
- La **liseuse** du fanzine (F-04) et le **chat** (F-13) demandent une réactivité en quasi temps réel.

**Comment on la vérifie :** 95 % des requêtes API en moins de 300 ms, pages principales affichées en moins de 2,5 s (indicateur Web Vitals *LCP*), messages du chat reçus en moins d'1 s. Tests de charge à chaque release.

### 2.4 Scalabilité (structurant)

**Définition :** capacité du système à **augmenter (ou réduire) ses ressources** pour absorber une variation de charge tout en conservant ses performances. Elle peut être horizontale (ajout d'instances) ou verticale (instances plus puissantes). *Dans ISO 25010, elle relève de la capacité et de l'adaptabilité.*

**Pourquoi c'est essentiel ici :**
- **Pics prévisibles** (C-10) : le Petit Festival, la sortie des 4 numéros annuels du fanzine, les campagnes de crowdfunding et les sorties d'**exclusivités Evil Ed** (F-02, éditions limitées avec une ruée sur le site).
- **Croissance prévue** : V2 avec les enchères (beaucoup d'enchères concurrentes en fin de vente) et la diffusion vidéo ; V3 avec le streaming du festival en accès limité (C-14).
- Pour une petite structure, **payer la capacité maximale toute l'année n'est pas raisonnable** : il faut une élasticité.

**Comment on la vérifie :** tenir **10 fois le trafic moyen** sans dégrader les temps de réponse au-delà des seuils de 2.3, mise à l'échelle automatique validée en test de charge, retour automatique à la normale après le pic.

### 2.5 Accessibilité (structurant)

**Définition (ISO 25010, au sein de l'utilisabilité) :** capacité du produit à être utilisé par des personnes ayant **la plus grande variété de caractéristiques et de capacités** (handicaps visuels, auditifs, moteurs, cognitifs). En France, le référentiel est le **RGAA** (Référentiel Général d'Amélioration de l'Accessibilité), aligné sur les **WCAG 2.1 niveau AA**.

**Pourquoi c'est essentiel ici :**
- **Exigence explicite** du contexte (C-01).
- **Obligation légale** : depuis juin 2025, l'European Accessibility Act impose l'accessibilité aux services de **commerce électronique**.
- Le public visé inclut des lecteurs (fanzine, BD) : la **liseuse** (F-04) doit être compatible avec les lecteurs d'écran et le zoom.
- L'accessibilité améliore aussi l'**ergonomie pour tous** (C-02) et le référencement.

**Comment on la vérifie :** audits automatiques dans le pipeline (aucune erreur bloquante), audit RGAA manuel avant la mise en production avec un objectif de **≥ 75 % de conformité en V1 et 100 % des critères AA en cible**, déclaration d'accessibilité publiée.

### 2.6 Maintenabilité (durable)

**Définition (ISO 25010) :** facilité avec laquelle le produit peut être modifié pour être corrigé, amélioré ou adapté. Elle regroupe :
- **Modularité :** un changement sur un composant a un impact minimal sur les autres.
- **Réutilisabilité :** des composants peuvent servir dans plusieurs contextes.
- **Analysabilité :** on diagnostique facilement une anomalie ou l'impact d'un changement.
- **Modifiabilité :** on modifie sans introduire de défauts.
- **Testabilité :** on vérifie facilement qu'une modification fonctionne.

**Pourquoi c'est essentiel ici :**
- **Équipe réduite et junior** (1 architecte et 2 alternants, C-11) : le code doit être lisible, documenté et couvert par des tests pour que chacun puisse intervenir.
- **Feuille de route chargée** (V2 enchères et vidéo, V3 streaming, C-14) : il faut pouvoir ajouter des modules sans tout réécrire.
- **Rotation probable** de l'équipe (alternants, nouvelles embauches) : il faut limiter la dépendance à une seule personne, l'erreur du SI actuel.

**Comment on la vérifie :** couverture de tests ≥ 70 % sur le code métier, aucun problème bloquant à l'analyse statique, revue de code obligatoire sur chaque modification, *lead time* (du commit à la production) inférieur à 1 jour.

### 2.7 Interopérabilité (durable)

**Définition (ISO 25010, au sein de la compatibilité) :** capacité de plusieurs systèmes à **échanger des informations et à utiliser celles qui ont été échangées**, au moyen de formats et de protocoles standardisés.

**Pourquoi c'est essentiel ici :**
- **SI hétérogène** (C-05) : gestion de stock, fournisseurs, CRM et caisses fonctionnent séparément et échangent par **fichiers CSV manuels**.
- **Stock par magasin** (C-06) : pour vendre en ligne sans survente, la plateforme doit connaître en continu les stocks des 4 magasins et déclencher des transferts.
- **Services externes** à intégrer : paiement, transporteur La Poste (suivi des colis, F-16), emailing.
- **Évolutions** : intégrer plus tard le site Evil Ed et les plateformes de crowdfunding.

**Comment on la vérifie :** stocks synchronisés avec un décalage de moins de 5 minutes, **0 échange CSV manuel** pour les flux couverts par la plateforme, API documentées selon un standard (par exemple OpenAPI) et versionnées.

---

## 3. Tensions et arbitrages entre attributs

| Tension | Explication | Arbitrage retenu |
|---|---|---|
| **Sécurité ↔ Performance** | Chiffrement, contrôles d'autorisation et scans ajoutent de la latence | Sécurité prioritaire. On compense par du cache sur les **contenus publics** (news, catalogue) et par le chiffrement en périphérie (TLS) |
| **Sécurité ↔ Utilisabilité / accessibilité** | Une authentification forte ou un captcha peuvent gêner, voire exclure (captcha visuel inaccessible) | MFA **obligatoire pour l'admin**, **proposée** aux clients. Protection anti-robots **sans captcha visuel** ou avec une alternative accessible |
| **Performance ↔ Maintenabilité** | Les optimisations poussées complexifient le code | On optimise **uniquement les points mesurés comme lents**. La lisibilité reste la règle par défaut |
| **Scalabilité ↔ Coût / simplicité** | Une architecture distribuée et élastique est plus complexe à opérer pour une petite équipe | Découpage **modéré** (quelques composants par domaine, pas de micro-services à outrance) et **services managés** pour réduire la charge d'exploitation |
| **Disponibilité ↔ Cohérence des données** | En cas de panne réseau, on choisit entre refuser des ventes ou risquer une survente | **Cohérence forte** sur le paiement et la réservation du stock. **Cohérence à terme** acceptée pour les recommandations, les notifications et les compteurs |
| **Interopérabilité ↔ Sécurité** | Ouvrir des API vers le SI existant agrandit la surface d'attaque | Les API d'intégration sont authentifiées, limitées en débit et **non exposées publiquement** |
| **Recommandations personnalisées ↔ Confidentialité (RGPD)** | Les recommandations comportementales (F-09) demandent de collecter des données de navigation | **Consentement explicite** (opt-in), réglages dans l'espace utilisateur (F-10), minimisation et durée de conservation limitée |

---

## 4. Lien avec la suite

- **US-02.2 (cycle DevSecOps) :** chaque attribut a un **contrôle automatique** dans le pipeline (scans de sécurité, tests de charge, audits d'accessibilité, analyse statique).
- **EPIC 03 (architecture) :** la scalabilité, la disponibilité et l'interopérabilité orientent le découpage en composants (isolation des pannes, bus d'intégration).
- **EPIC 05 (technologies) :** les critères de comparaison des deux solutions doivent reprendre ces attributs.
- **EPIC 06 (tests) :** les indicateurs de vérification ci-dessus deviennent des critères d'acceptation des tests.

---

[← Mise en place du suivi commun](../cadrage/suivi-du-projet.md) · [Sommaire](../README.md) · [Cycle de vie DevSecOps →](cycle-devsecops.md)
