# Positionnement des tests dans le pipeline CI/CD

> **Story :** US-06.3 · **Jira :** [SCRUM-33](https://maalsi25.atlassian.net/browse/SCRUM-33) · **Epic :** EPIC 06, Environnement managé et stratégie de tests
> **Responsable :** Membre D · **Binôme :** Membre B
> **Entrées :** [US-06.2, catégories de tests](categories-de-tests.md) · [US-04.4, choix CI/CD](../cicd/comparaison-et-choix.md) · [US-02.2, cycle DevSecOps](../qualite-devsecops/cycle-devsecops.md)

**But :** placer chaque famille de tests **à l'étape du pipeline où elle est la plus utile**, et rendre explicites les **conséquences d'un échec**. Le focus est la **stratégie**, pas le catalogue d'outils.

---

## 1. Schéma du pipeline et des tests

> Schéma original réalisé par le groupe. Le source Mermaid ci-dessous sert de référence et est redessiné dans le support PPT.

```mermaid
flowchart LR
    subgraph S0["⓪ Poste du développeur"]
        A0["lint · unitaires<br/>détection de secrets<br/>(avant commit)"]
    end
    subgraph S1["① Pull request · < 10 min"]
        A1["secrets · lint · SAST · SCA<br/>unitaires + couverture<br/>contrat"]
    end
    subgraph S2["② Build · < 5 min"]
        A2["image conteneur<br/>scan d'image · scan IaC<br/>SBOM · smoke test"]
    end
    subgraph S3["③ Intégration · < 20 min"]
        A3["intégration (base, bus)<br/>e2e parcours critiques<br/>accessibilité automatique<br/>DAST"]
    end
    subgraph S4["④ Staging · release"]
        A4["performance · charge ×10<br/>audit RGAA manuel<br/>recette PO · go / no-go"]
    end
    subgraph S5["⑤ Production"]
        A5["canary + smoke test<br/>supervision continue<br/>résilience · restauration"]
    end

    S0 --> S1 -->|"fusion autorisée"| S2 --> S3 --> S4 -->|"go"| S5
    S1 -. " fusion refusée" .-> S0
    S2 -. " image non publiée" .-> S0
    S3 -. " pas de promotion" .-> S0
    S4 -. " no-go" .-> S0
    S5 -. "↩ rollback automatique" .-> S4
```

**Logique :** les tests **rapides et nombreux** sont exécutés **à chaque modification**. Les tests **lents et coûteux** sont exécutés **moins souvent**, sur un environnement proche de la production. Un défaut est arrêté **le plus tôt possible**, quand sa correction coûte le moins.

---

## 2. Tableau de positionnement

| Étape | Déclencheur | Tests exécutés | Durée cible | Si un test échoue… | Qui est alerté |
|---|---|---|---|---|---|
| **⓪ Poste** | Avant chaque commit (hook) | Lint, unitaires du module modifié, détection de secrets | Secondes | Le commit est refusé localement | Le développeur |
| **① Pull request** | Chaque PR | Secrets, lint, **SAST**, **SCA**, **unitaires + couverture**, **contrat** | < 10 min | **La fusion est impossible** (statut rouge sur la PR) | Auteur de la PR |
| **② Build** | Fusion sur `main` | Build de l'image, **scan d'image et d'IaC**, SBOM, **smoke test** de l'image | < 5 min | L'image **n'est pas publiée** dans le registre | Auteur + DevOps |
| **③ Intégration** | Chaque image publiée | **Intégration** (base, bus d'événements, connecteur SI), **e2e** des parcours critiques, **accessibilité automatique**, **DAST** | < 20 min | **Pas de promotion** vers le staging | Équipe (canal `#ci`) |
| **④ Staging** | Release candidate (hebdomadaire) et **avant chaque pic connu** | **Performance**, **charge ×10** et endurance, **audit RGAA manuel** (échantillon), recette fonctionnelle | Heures | **No-go** : la release est reportée | PO + équipe |
| **⑤ Production** | Après go du PO | Déploiement **canary** + **smoke test**, puis supervision. Résilience et restauration **planifiées** (mensuelles) | Minutes, puis continu | ↩ **Rollback automatique** si le smoke test échoue ou si le taux d'erreur augmente | DevOps d'astreinte |

---

## 3. Lien entre les tests et les exigences de qualité

| Exigence (US-02.1) | Seuil | Étape du pipeline qui le vérifie |
|---|---|---|
| 0 vulnérabilité critique ou haute | SAST, SCA, scan d'image, DAST | ①, ②, ③ |
| Couverture ≥ 70 % du code métier | Unitaires | ① |
| p95 des API < 300 ms, LCP < 2,5 s | Performance | ④ |
| ×10 le trafic moyen sans dégradation | Charge | ④ (et avant chaque pic) |
| 0 erreur d'accessibilité bloquante | Accessibilité automatique | ③ |
| ≥ 75 % de conformité RGAA | Audit manuel | ④ |
| Disponibilité 99,5 %, RTO ≤ 4 h | Smoke, canary, résilience, restauration | ⑤ |
| Stocks synchronisés en moins de 5 min | Intégration (connecteur SI) | ③ |

---

## 4. Ce qui est déjà démontré

Le pipeline de démonstration de l'EPIC 04 livre la **boutique de démonstration** ([`apps/` et `infra/`](../../README.md)). Il implémente déjà les étapes **① et ②**, à l'identique sur GitHub Actions et Jenkins :

| Étape | Tests de la démo | Démontré |
|---|---|---|
| ① | Secrets (gitleaks), SAST (Semgrep), SCA (Trivy sur les dépendances Maven et npm) | Scénario `secret` : clé d'API détectée en 8 s, **livraison bloquée** |
| ① | Backend : 23 tests unitaires et d'intégration (MockMvc, base H2, binder de test du bus), couverture ≥ 70 % par service (JaCoCo) | Scénario `regression` : 2 tests rouges, **images non construites** (37 s) |
| ① | Front : 10 tests de composants (Vitest, Testing Library), couverture ≥ 70 % | OK |
| ② | Scan des 9 images (Trivy), avec registre d'exceptions justifiées et datées | A bloqué Spring Boot 3.4 (failles critiques) et imposé la migration vers Spring Boot 4.0 |
| ② | **Test de bout en bout** : la boutique complète démarre, un parcours client est joué (connexion, commande, événement reçu par le bus, accès refusé sans jeton, seconde passerelle) | 9 vérifications en 44 s |
| ③ | Résilience (en démo, hors pipeline) : panne d'un service, d'un consommateur, rejeu, message poison | Scénarios `tools/scenarios/bus.py` et `tools/scenarios/passerelle.py` (US-05.2 à US-05.5) |
| ⑤ | Sondes de santé, auto-réparation, mise à jour sans coupure | Démo Kubernetes ([US-06.1](architecture-kubernetes.md)) |

**Pistes pour aller plus loin :** les scénarios de panne (`tools/scenarios/passerelle.py`) sont automatisés et rejouables : ils peuvent devenir l'étape ③ « tests de résilience » du pipeline, exécutée chaque nuit.

---

## 5. Règles de gouvernance des tests

- **Un test bloquant ne se contourne pas.** Toute exception (faux positif SAST, CVE sans correctif) est **documentée**, validée par le Security Champion, et a une **date d'expiration**.
- **Les tests instables** (*flaky*) sont mis en quarantaine **et** une story de correction est créée : un pipeline auquel on ne croit plus n'arrête plus rien.
- **Les seuils évoluent** à chaque rétrospective, en fonction des incidents de production (boucle d'amélioration continue, [US-07.4](../securite/amelioration-continue.md)).
- **Durée totale ① + ② inférieure à 15 min**, sinon les développeurs contournent le pipeline. Les tests lents sont déplacés vers ③ ou ④.

---

[← Catégories de tests](categories-de-tests.md) · [Sommaire](../README.md) · [Démarche d'inventaire applicatif →](../securite/inventaire-du-parc.md)
