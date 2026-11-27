# Répartition des rôles et des tâches

> **Story :** US-01.2 · **Jira :** [SCRUM-15](https://maalsi25.atlassian.net/browse/SCRUM-15) · **Epic :** EPIC 01, Cadrage et organisation du groupe
> **Objectif :** donner une responsabilité claire sur chaque chantier pour limiter les doublons et les oublis.
> **Groupe :** 4 membres, désignés **Membre A, B, C et D**.

---

## 1. Rôles transverses

| Rôle | Titulaire | Responsabilités |
|---|---|---|
| **Coordinateur / Scrum Master** | Membre A | Anime les points de synchronisation, tient le board Jira à jour, surveille les jalons J1 à J6 et lève les blocages |
| **Responsable technique (démos)** | Membre B | Cohérence des environnements de démonstration (dépôt Git, pipelines, cluster local), aide technique transverse |
| **Responsable support de soutenance** | Membre C | Gabarit du PPT, intégration des messages clés de chaque epic, cohérence du discours |
| **Responsable qualité documentaire** | Membre D | Charte des schémas (faits maison), respect de la *Definition of Done*, cohérence des livrables `docs/` |

Ces rôles s'ajoutent au pilotage des epics. Ils ne le remplacent pas.

---

## 2. Pilote et binôme par epic

**Règle :** le **pilote** est responsable de la livraison de l'epic. Le **binôme** relit et valide chaque livrable avant qu'il passe en « Terminé » (voir [US-01.3](suivi-du-projet.md)).

| Epic | Intitulé | Jours | Pilote | Binôme / relecteur | Justification |
|---|---|---|---|---|---|
| [EPIC 01](https://maalsi25.atlassian.net/browse/SCRUM-6) | Cadrage et organisation du groupe | J1 | **Membre A** | Membre B | Rôle de coordinateur |
| [EPIC 02](https://maalsi25.atlassian.net/browse/SCRUM-7) | Qualité logicielle et démarche DevSecOps | J2 | **Membre B** | Membre D | Prépare le pipeline CI/CD (EPIC 04) |
| [EPIC 03](https://maalsi25.atlassian.net/browse/SCRUM-8) | Architecture macroscopique | J2 | **Membre A** | Membre C | S'appuie sur la synthèse du besoin (US-01.1) |
| [EPIC 04](https://maalsi25.atlassian.net/browse/SCRUM-9) | Comparaison et démo de 2 solutions CI/CD | J3-J5 | **Membre B** | Membre D | Continuité avec le cycle DevSecOps |
| [EPIC 05](https://maalsi25.atlassian.net/browse/SCRUM-10) | Comparaison et démo de 2 technologies applicatives | J3-J5 | **Membre C** | Membre B | Démo lourde, portée par une personne dédiée |
| [EPIC 06](https://maalsi25.atlassian.net/browse/SCRUM-11) | Environnement managé et stratégie de tests | J5 | **Membre D** | Membre B | D a participé au 2nd outil CI/CD, où se placent les tests |
| [EPIC 07](https://maalsi25.atlassian.net/browse/SCRUM-12) | Politique de sécurité et amélioration continue | J5 | **Membre C** | Membre D | C est libre après les démos de J4 |
| [EPIC 08](https://maalsi25.atlassian.net/browse/SCRUM-13) | Synthèse, soutenance et REX | J5-J6 | **Membre A** | Membre C | Rôle de coordinateur, vue d'ensemble |

**Équilibre de charge :**

| Membre | Epics pilotées | Binôme de | Renforts ponctuels |
|---|---|---|---|
| A | 01, 03, 08 (transverses, plutôt légères) | — | US-05.3 (démo techno n°2) |
| B | 02, 04 (enchaînement DevSecOps → CI/CD) | 01, 05, 06 | US-07.3 (supervision) |
| C | 05, 07 (démo lourde, puis sécurité) | 03, 08 | — |
| D | 06 | 02, 04, 07 | US-02.3 (métiers), US-04.3 (démo CI/CD n°2), US-05.5 (passerelle d'API) |

---

## 3. Répartition des stories par jalon

Le responsable d'une story est par défaut le pilote de son epic, sauf mention *(renfort)*.

### J1 : formation du groupe et prise en main du sujet

| Story | Responsable | Dépendances |
|---|---|---|
| [US-01.1](https://maalsi25.atlassian.net/browse/SCRUM-14) Synthétiser le besoin | Membre A | — |
| [US-01.2](https://maalsi25.atlassian.net/browse/SCRUM-15) Répartir les rôles et tâches | Membre A | — |
| [US-01.3](https://maalsi25.atlassian.net/browse/SCRUM-16) Mettre en place le suivi commun | Membre A | US-01.2 |

> Tout le groupe lit le sujet en J1. US-01.1 est relue collectivement, car elle conditionne toutes les autres stories.

### J2 : démarche de développement et schéma logique → *livrable : la démarche de développement*

| Story | Responsable | Dépendances |
|---|---|---|
| [US-02.1](https://maalsi25.atlassian.net/browse/SCRUM-17) Définir les attributs de qualité | Membre B | US-01.1 |
| [US-02.2](https://maalsi25.atlassian.net/browse/SCRUM-18) Schématiser le cycle DevSecOps | Membre B | US-02.1 |
| [US-02.3](https://maalsi25.atlassian.net/browse/SCRUM-19) Décrire les métiers et leurs interactions | **Membre D** *(renfort)* | US-02.2 |
| [US-03.1](https://maalsi25.atlassian.net/browse/SCRUM-20) Identifier les composants fonctionnels | Membre A | US-01.1 |
| [US-03.2](https://maalsi25.atlassian.net/browse/SCRUM-21) Dessiner l'architecture macroscopique | Membre A | US-03.1 |
| [US-03.3](https://maalsi25.atlassian.net/browse/SCRUM-22) Vérifier la couverture du besoin | **Membre C** *(renfort)* | US-03.2, US-01.1 |

> Membre C profite aussi de J2 pour **pré-étudier les domaines techniques** candidats de l'EPIC 05.

### J3 : choix des solutions et démarrage des démos

| Story | Responsable | Dépendances |
|---|---|---|
| [US-04.1](https://maalsi25.atlassian.net/browse/SCRUM-23) Sélectionner les 2 candidats CI/CD et les critères | Membre B | US-02.2 |
| [US-05.1](https://maalsi25.atlassian.net/browse/SCRUM-27) Choisir un domaine technique à comparer | Membre C | US-03.2 |
| [US-04.2](https://maalsi25.atlassian.net/browse/SCRUM-24) Démo du 1er outil CI/CD | Membre B | US-04.1 |
| [US-04.3](https://maalsi25.atlassian.net/browse/SCRUM-25) Démo du 2nd outil CI/CD | **Membre D** *(renfort)* | US-04.1 |
| [US-05.2](https://maalsi25.atlassian.net/browse/SCRUM-28) Démontrer la 1re technologie | Membre C | US-05.1 |
| [US-05.3](https://maalsi25.atlassian.net/browse/SCRUM-29) Démontrer la 2nde technologie | **Membre A** *(renfort)* | US-05.1 |

> **Point de décision J3 :** le choix des outils CI/CD et du domaine technique se valide **en groupe**, lors de la synchronisation de fin de matinée, avant de démarrer les démos.
> Avec 4 personnes, **les 4 démos avancent en parallèle** (une par membre).

### J4 : poursuite des démonstrations et conclusions

| Story | Responsable | Dépendances |
|---|---|---|
| US-04.2 / US-04.3 / US-05.2 / US-05.3 *(suite et fin)* | B / D / C / A | — |
| [US-04.4](https://maalsi25.atlassian.net/browse/SCRUM-26) Conclusion comparative CI/CD | Membre B, avec D | US-04.2, US-04.3 |
| [US-05.4](https://maalsi25.atlassian.net/browse/SCRUM-30) Argumenter le choix technique | Membre C, avec A | US-05.2, US-05.3 |
| US-05.5 Comparer deux passerelles d'API (solution technique n°2) | **Membre D** | US-03.1, US-05.1 |

### J5 : finalisation → *livrables : démos finalisées, schémas finalisés, plan de sécurité*

| Story | Responsable | Dépendances |
|---|---|---|
| [US-06.1](https://maalsi25.atlassian.net/browse/SCRUM-31) Expliquer l'architecture de l'orchestrateur | Membre D | US-05.1 (si Kubernetes est retenu) |
| [US-06.2](https://maalsi25.atlassian.net/browse/SCRUM-32) Définir les catégories de tests | Membre D | US-02.1 |
| [US-06.3](https://maalsi25.atlassian.net/browse/SCRUM-33) Positionner les tests dans le CI/CD | Membre D | US-06.2, US-04.4 |
| [US-07.1](https://maalsi25.atlassian.net/browse/SCRUM-34) Démarche d'inventaire applicatif | Membre C | US-01.1 |
| [US-07.2](https://maalsi25.atlassian.net/browse/SCRUM-35) Contrôles et scans de sécurité | Membre C | US-04.4 |
| [US-07.3](https://maalsi25.atlassian.net/browse/SCRUM-36) Supervision et réaction aux incidents | **Membre B** *(renfort)* | US-07.1 |
| [US-07.4](https://maalsi25.atlassian.net/browse/SCRUM-37) Organiser l'amélioration continue | Membre C | US-07.2, US-07.3 |
| [US-08.1](https://maalsi25.atlassian.net/browse/SCRUM-38) Consolider la recommandation globale | Membre A | Toutes les epics 02 à 07 |
| [US-08.2](https://maalsi25.atlassian.net/browse/SCRUM-39) Scénariser les démonstrations | Membre A, avec les 4 orateurs | US-04.4, US-05.4 |
| [US-08.3](https://maalsi25.atlassian.net/browse/SCRUM-40) Préparer l'organisation et le REX | Membre A | US-01.2, US-01.3 |

### J6 : soutenance (20 min + 15 min de Q/R)

| Story | Responsable | Dépendances |
|---|---|---|
| [US-08.4](https://maalsi25.atlassian.net/browse/SCRUM-41) Répéter la soutenance et préparer les questions | **Tout le groupe** | US-08.1 à US-08.3 |

**Répartition de la parole (indicative) :** A pour l'intro, l'organisation et la conclusion/REX ; B pour la démarche DevSecOps et la démo CI/CD n°1 ; D pour la démo CI/CD n°2, l'orchestrateur et les tests ; C pour l'architecture, les démos technologiques et la sécurité. Chacun présente au moins une démo.

---

## 4. Chemin critique et dépendances

```
US-01.1 ──┬─► US-02.1 ─► US-02.2 ─┬─► US-02.3
          │ └─► US-04.1 ─┬─► US-04.2 (B) ─┐
          │ └─► US-04.3 (D) ─┴─► US-04.4 ─┬─► US-06.3
          │ └─► US-07.2 ─┐
          ├─► US-03.1 ─► US-03.2 ─┬─► US-03.3 │
          │ └─► US-05.1 ─┬─► US-05.2 (C) ─┐ │
          │ └─► US-05.3 (A) ─┴─► US-05.4 ──────────────┤
          └─► US-07.1 ─► US-07.3 ─────────────────────────────────────────────► US-07.4 ◄─┘
                                                                                    │
                                             US-08.1 / US-08.2 / US-08.3 ◄──────────┘
                                                        │
                                                     US-08.4 (J6)
```

**Chemin critique :** US-01.1 → US-02.2 → US-04.1 → démos CI/CD → US-04.4 → US-08.2 → US-08.4.
Les démos (EPIC 04 et 05) sont le principal **risque de retard** : elles comptent pour au moins 10 minutes de la soutenance. C'est pourquoi chacun des 4 membres en porte une.

---

## 5. Outils collaboratifs

| Outil | Usage | Règle d'usage |
|---|---|---|
| **Jira** (board SCRUM, projet BLOC3) | Backlog, sprint, suivi des stories | Une story = un ticket. Les labels `J1` à `J6` donnent le jalon, `P0`/`P1` la priorité. Le ticket est mis à jour à chaque changement de statut |
| **Dépôt Git** (GitHub et/ou GitLab) | Documents Markdown (`docs/`), code et config des démos | Une branche par story, fusion par *pull/merge request* relue par le binôme. Le dépôt sert aussi de support aux démos CI/CD |
| **Markdown** (`docs/`) | Livrables écrits, un fichier par story | Nommage : `docs/<epic>/US-xx.y_<sujet>.md` |
| **draw.io / Excalidraw** | Schémas (DevSecOps, architecture, orchestrateur) | Schémas **faits maison** (consigne). Sources versionnées dans le dépôt |
| **PowerPoint / Google Slides** | Support de soutenance | Gabarit unique tenu par Membre C. Une section par epic |
| **Discord / Teams** | Communication synchrone et asynchrone | Un canal par thème (`#général`, `#démos`, `#blocages`). Le compte rendu de chaque point de synchronisation est posté dans `#général` |

---

## 6. Plan de repli (absence d'un membre)

- **Absence courte (moins d'une demi-journée) :** le binôme reprend les stories en cours de l'absent.
- **Absence longue :** le coordinateur réaffecte. Les démos restent prioritaires (`P0`). Si besoin, la démo CI/CD n°2 (D) ou la démo techno n°2 (A) est reprise par le pilote de l'epic correspondante.


---

## 7. Répartition de la parole en soutenance

Chaque comparaison est présentée par la personne qui l'a menée, et une personne porte la vision d'ensemble du début à la fin. Le détail minuté est dans le [déroulé de la soutenance](../soutenance/deroule-de-la-soutenance.md).

| Membre | Présente | Démos |
|---|---|---|
| **A** | Vision d'ensemble : besoin, qualité, architecture, DevSecOps, Kubernetes, tests, sécurité, recommandation et bilan | Kubernetes |
| **B** | Comparaison CI/CD : GitHub Actions et Jenkins + Argo CD | GitHub Actions, Jenkins + Argo CD |
| **C** | Solution technique n°1 : bus d'événements, RabbitMQ et Kafka | RabbitMQ, Kafka |
| **D** | Solution technique n°2 : passerelle d'API, Spring Cloud Gateway et Kong | Spring Cloud Gateway et Kong |

---

[← Synthèse du besoin de l'entreprise](synthese-du-besoin.md) · [Sommaire](../README.md) · [Mise en place du suivi commun →](suivi-du-projet.md)
