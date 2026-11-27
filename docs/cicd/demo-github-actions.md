# Démonstration du premier outil : GitHub Actions

> **Story :** US-04.2 · **Jira :** [SCRUM-24](https://maalsi25.atlassian.net/browse/SCRUM-24) · **Epic :** EPIC 04, Comparaison et démonstration de deux solutions CI/CD
> **Responsable :** Membre B · **Binôme :** Membre D
> **Scénario de référence :** [US-04.1](candidats-et-criteres.md) · **Application :** [boutique de démonstration](../../README.md) · **Pipeline :** [`.github/workflows/boutique.yml`](../../.github/workflows/boutique.yml)

---

## 1. Contenu de la démo

| Élément | Fichier |
|---|---|
| Application livrée : **boutique front + microservices** (support identique aux deux outils) | `apps/front/`, `apps/back/`, `infra/kong/`, `infra/postgres/` |
| Pipeline GitHub Actions | `.github/workflows/ci.yml` |
| Étapes communes aux deux outils | `infra/ci/scan-images.sh` (scan des images), `infra/ci/smoke-test.sh` + `infra/ci/smoke.py` (test de bout en bout) |
| Registre des vulnérabilités acceptées | `.trivyignore.yaml` |
| Scénarios d'échec | `tools/demo/scenario.sh` |
| Procédure complète | [`README.md` de la boutique](../../README.md), section 4 |

La boutique est poussée dans **son propre dépôt GitHub** (README, section 4). Le pipeline livre la **vraie application de démonstration** : 9 images (front, passerelle, 5 services Spring Boot, Kong, PostgreSQL).

---

## 2. Structure du pipeline

```mermaid
flowchart LR
    E(["push main / PR / manuel"]) --> S & B & F & A
    S["Job secrets<br/>gitleaks"]
    B["Job backend<br/>Maven : 23 tests<br/>couverture ≥ 70 %<br/> rapports"]
    F["Job front<br/>Vitest : 10 tests<br/>couverture ≥ 70 %"]
    A["Job sast-sca<br/>Semgrep · Trivy fs"]
    S & B & F & A --> I["Job images<br/>build 9 images → scan Trivy<br/>→ test de bout en bout<br/>→ push GHCR (main)"]
```

| Concept GitHub Actions | Utilisation dans la démo |
|---|---|
| **Workflow** (`on:`) | Déclenché par `push` sur `main`, `pull_request` et `workflow_dispatch` (bouton manuel) |
| **Jobs** | 5 jobs. Les 4 premiers tournent **en parallèle** sur des runners distincts |
| **`needs:`** | Les images ne sont construites que si les 4 jobs de qualité sont verts : c'est la **quality gate** |
| **Actions du marketplace** | `actions/checkout`, `actions/setup-java` et `actions/setup-node` (avec **cache Maven et npm**), `actions/upload-artifact`, `docker/login-action` |
| **`permissions:`** | Lecture seule par défaut. `packages: write` est accordé **uniquement** au job de publication (moindre privilège) |
| **`secrets.GITHUB_TOKEN`** | Jeton éphémère généré par GitHub pour publier sur GHCR. **Aucun secret à créer** |
| **`$GITHUB_STEP_SUMMARY`** | Résumé des tests et des images publiées affiché sur la page du run |
| **`if:`** | La publication n'a lieu que sur un `push` vers `main`, jamais sur une PR |

---

## 3. Déroulé de la démonstration (environ 3 min)

| # | Action | Ce que la direction voit |
|---|---|---|
| 1 | Montrer `ci.yml` dans le dépôt | Le pipeline est **du code**, versionné et relu comme le reste |
| 2 | Pousser un commit sur `main` (ou *Run workflow*) | **Déclenchement** immédiat dans l'onglet *Actions* |
| 3 | Ouvrir le run | Graphe des **4 jobs parallèles** puis du job images, avec le statut en temps réel |
| 4 | Ouvrir le job images, étape « test de bout en bout » | La **boutique complète** démarre dans le runner : connexion, commande, notification reçue par le bus |
| 5 | Montrer *Packages* | **Résultat** : les 9 images versionnées sont publiées dans GHCR |
| 6 | `sh tools/demo/scenario.sh regression` → commit → push | Le job **backend** passe au rouge et les **images ne sont pas construites** |
| 7 | Ouvrir une PR avec la régression | Le **statut rouge s'affiche directement sur la PR** : on ne peut pas fusionner en confiance |

---

## 4. Contrôles du pipeline et comportement attendu

| Contrôle | Outil | Bloque la livraison si… |
|---|---|---|
| Syntaxe et expressions du workflow | `actionlint` (avec shellcheck), avant chaque push | erreur de syntaxe ou d'expression |
| Backend : tests et couverture | Maven via turbo, Spring Boot 4 | un test échoue ou la couverture d'un service passe sous 70 % |
| Front : tests et couverture | Vitest via turbo | un test échoue ou la couverture passe sous 70 % |
| SAST | Semgrep (règles Java, React et secrets) | alerte de sévérité ERROR |
| SCA | Trivy (dépendances Maven et npm) | vulnérabilité critique corrigeable |
| Secrets | gitleaks | secret détecté |
| Images | Trivy sur les 9 images | vulnérabilité critique corrigeable, hors exception justifiée et datée (`.trivyignore.yaml`, voir [US-07.4](../securite/amelioration-continue.md)) |
| Test de bout en bout | Boutique complète démarrée dans le runner, parcours client | une étape du parcours échoue |

Les scénarios `regression` et `secret` (`tools/demo/scenario.sh`) bloquent la livraison exactement comme dans Jenkins : mêmes commandes, mêmes images.

---

## 5. Mesures à relever pendant la démonstration

| Mesure | Ce qu'on observe |
|---|---|
| Temps de mise en place | De la création du dépôt au premier pipeline vert |
| Durée d'un pipeline | Premier lancement, puis lancements suivants (caches Maven et npm actifs) |
| Délai entre le push et le démarrage | Webhook natif de GitHub |
| Scénario `regression` | Temps jusqu'au signal rouge sur la PR |
| Scénario `secret` | La *push protection* de GitHub peut refuser le push avant même le pipeline |

---

## 6. Observations (forces et points de friction)

**Points forts constatés :**
- **Aucune infrastructure à installer** : le pipeline existe dès que le fichier YAML est poussé.
- **Intégration native au dépôt** : statut sur les PR, lien direct commit ↔ run, registre GHCR intégré, jeton éphémère.
- **Parallélisme naturel** : chaque job tourne sur un runner neuf (isolation forte, pas d'état résiduel).
- **Marketplace** : installation de Java et Node.js, cache et artefacts en une ligne chacun.
- **Moindre privilège** simple à exprimer (`permissions:` par job).

**Points de friction :**
- **Pas d'exécution locale native** : pour tester le workflow avant de le pousser, il faut des outils tiers ou multiplier les commits « fix CI ».
- **Runners hébergés aux États-Unis** par défaut (Azure) : le code, les logs et les artefacts transitent hors UE. Les runners **auto-hébergés en Europe** sont possibles, mais réintroduisent de la maintenance.
- **Actions tierces = risque de chaîne d'approvisionnement** : une action compromise exécute du code dans le pipeline. Bonne pratique : figer les actions par **SHA de commit** plutôt que par tag (`@v4`).
- **Quotas** de minutes gratuites sur les dépôts privés (2 000 min par mois en offre gratuite), au-delà facturé à la minute.
- **Dépendance forte à GitHub** (forge, CI, registre) : migrer vers une autre forge plus tard est coûteux.

---

[← Sélection des deux solutions CI/CD et des critères](candidats-et-criteres.md) · [Sommaire](../README.md) · [Démonstration du second outil : Jenkins →](demo-jenkins.md)
