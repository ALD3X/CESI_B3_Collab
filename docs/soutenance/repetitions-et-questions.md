# Répétition de la soutenance et préparation des questions

> **Story :** US-08.4 · **Jira :** [SCRUM-41](https://maalsi25.atlassian.net/browse/SCRUM-41) · **Epic :** EPIC 08, Synthèse, soutenance et retour d'expérience
> **Responsable :** tout le groupe
> **Entrées :** [US-08.1](recommandation-globale.md) · [US-08.2](deroule-de-la-soutenance.md) · [US-08.3](organisation-et-bilan.md)

**But :** tenir le format (**20 min + 15 min de questions**) et permettre à **chaque membre de défendre l'ensemble des choix**, pas seulement sa partie.

---

## 1. Protocole de répétition

| # | Répétition | Objectif | Critère de réussite |
|---|---|---|---|
| R1 | **À blanc, slides seules** (sans démo) | Fluidité des transitions, cohérence du discours | Chaque orateur tient son temps à ±15 s |
| R2 | **Complète, avec les démos en direct** | Tenir 20 min, enchaîner les démos | ≤ 20:00, 10 min de démo, aucune démo de plus de 15 s au-delà de son créneau |
| R3 | **Avec incidents simulés** (Internet coupé, une démo qui plante) | Basculer sur les vidéos sans perdre le fil | Bascule en moins de 15 s |
| R4 | **Questions croisées** : chaque membre répond à des questions **hors de sa partie** | Défendre les choix communs | Chaque membre répond correctement à 3 questions tirées au sort (§3) |

**Chronométrage :** noter dans le tableau ci-dessous l'écart à chaque repère.

| Répétition | 04:00 | 08:30 | 13:00 | 17:45 | Fin | Remarques |
|---|---|---|---|---|---|---|
| R1 | | | | | | |
| R2 | | | | | | |
| R3 | | | | | | |

---

## 2. Conseils d'animation (note individuelle)

- **S'adresser au jury comme à une direction :** commencer par le **message**, puis le détail. Exemple : « Les deux outils font le travail. Nous recommandons GitHub Actions, parce que… ».
- **Pendant une démo :** annoncer ce qu'on va voir, le montrer, puis dire ce qu'il fallait retenir.
- **Face à un imprévu :** le dire calmement, basculer sur le repli et poursuivre. *La réaction face à un imprévu est notée.*
- **Questions :** reformuler, répondre en 30 s, proposer d'approfondir. Si on ne sait pas : dire comment on vérifierait.
- **Passage de relais :** annoncer la personne suivante et son sujet.

---

## 3. Banque de questions probables

### CI/CD

| Question | Éléments de réponse |
|---|---|
| Pourquoi pas GitLab CI ? | Candidat crédible (forge et CI intégrées, auto-hébergeable en UE). Nous avons comparé deux **modèles opposés** (SaaS contre auto-hébergé) pour éclairer la décision. GitLab self-managed est notre alternative si la souveraineté devient une obligation (US-04.4) |
| GitHub Actions hors UE, n'est-ce pas contraire à C-04 ? | C-04 est un **souhait** (« aimerait »). Aucune donnée ni aucun secret de production dans la CI. Déploiement via un runner UE. Bascule possible, car les étapes sont portables (démontré) |
| Que se passe-t-il si une action tierce est compromise ? | Risque de chaîne d'approvisionnement : actions **figées par SHA**, liste d'actions autorisées, `permissions:` minimales par job, Dependabot |
| Comment faites-vous un rollback ? | Images immuables versionnées. Kubernetes : `rollout undo` ou retour à l'image précédente. Rollback automatique si le smoke test ou le canary échoue |

### Technologies (bus d'événements)

| Question | Éléments de réponse |
|---|---|
| Pourquoi pas Kafka, puisqu'il est plus rapide ? | 2 à 14 fois plus rapide, mais notre besoin est inférieur à 100 événements/s contre plus de 11 000 mesurés. Il est 6 fois plus lourd, demande 3 nœuds et coder la DLQ. Kafka redevient pertinent pour les enchères V2 (analyse de sensibilité) |
| Comment ferez-vous les recommandations sans rejeu ? | Les événements sont **archivés** (stockage ou entrepôt). RabbitMQ Streams est possible. Les contrats versionnés permettent de changer de broker |
| Vos mesures sont-elles fiables ? | Elles **comparent**, elles ne dimensionnent pas : poste unique, client dans le réseau Docker, 3 passes cohérentes, biais identifiés et corrigés (US-08.3) |
| Comment garantissez-vous qu'une commande n'est pas traitée deux fois ? | Livraison « au moins une fois » : les consommateurs sont **idempotents** (identifiant d'événement mémorisé). Côté Kafka, le producteur est idempotent |

### Architecture et Kubernetes

| Question | Éléments de réponse |
|---|---|
| Que se passe-t-il si etcd tombe ? | Plus aucune modification du cluster possible, mais **les applications continuent**. En offre managée, etcd est répliqué (3 membres, consensus) et sauvegardé par l'hébergeur |
| Différence entre kubelet et kube-proxy ? | Le kubelet fait démarrer et surveille les pods de son nœud. kube-proxy programme le réseau pour qu'un Service répartisse le trafic vers les pods sains |
| Pourquoi pas des micro-services ? | Découpage **modéré** par domaine : une petite équipe ne peut pas exploiter des dizaines de services (arbitrage de US-02.1 §3) |
| Où sont les bases de données ? | Une base par service (cloisonnement). De préférence en **service managé UE** hors du cluster. Le schéma ne nomme pas les moteurs, conformément à la consigne |
| Comment absorbez-vous un pic ? | Cache EN-1, services sans état, HPA (2 à 6 instances), traitements lourds en asynchrone via le bus, test de charge ×10 avant chaque pic, gel des déploiements |

### Qualité, tests et sécurité

| Question | Éléments de réponse |
|---|---|
| Pourquoi 70 % de couverture et pas 100 % ? | Le rendement décroît. On cible le **code métier**. La couverture ne garantit pas la qualité, d'où les tests de contrat, d'intégration et e2e en complément |
| Comment testez-vous l'accessibilité ? | Audit automatique dans le pipeline (bloquant) et audit manuel RGAA avant release. Un design system conforme dès la conception (UX) |
| Que faites-vous d'une CVE sans correctif ? | Exception documentée avec date d'expiration, et mesure compensatoire (WAF, désactivation, isolement réseau) |
| Fuite de données clients : que faites-vous ? | Processus P1 : confinement, qualification avec le DPO, **notification à la CNIL sous 72 h**, information des personnes si le risque est élevé, post-mortem |
| Et le SI existant, peu sécurisé ? | Inclus dans la politique : MFA sur le VPN et Gmail, sauvegarde immuable, scan mensuel, remplacement des CSV par le connecteur IN-1 (US-07.1 §4) |
| Pourquoi ne pas recruter un ingénieur sécurité ? | Pas de temps plein justifié : Security Champion interne + RSSI externe + automatisation du pipeline (US-02.3) |

### Organisation

| Question | Éléments de réponse |
|---|---|
| Qui a fait quoi ? | Tableau des pilotes et binômes (US-01.2). Chaque comparaison est présentée par la personne qui l'a menée : B la CI/CD, C le bus d'événements, D la passerelle. A porte la vision d'ensemble |
| Qu'est-ce que vous referiez autrement ? | Mesurer plus tôt, sur une machine de référence commune ; exécuter la CI réelle plus tôt (US-08.3 §2.3) |

---

## 4. Checklist finale (jour J)

- [ ] R1 à R4 réalisées, temps reportés au §1.
- [ ] Chaque membre a répondu à au moins 3 questions hors de sa partie.
- [ ] Préparation technique de [US-08.2](deroule-de-la-soutenance.md) §3 faite (J-1 et H-1).
- [ ] Vidéos de secours sur 2 ordinateurs et une clé USB.
- [ ] Support PPT final relu (schémas faits maison, une idée par slide, police lisible).

---

[← Organisation du groupe et retour d'expérience](organisation-et-bilan.md) · [Sommaire](../README.md)
