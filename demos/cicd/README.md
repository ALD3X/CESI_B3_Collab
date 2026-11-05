# Démo CI/CD : GitHub Actions et Jenkins

Mini-service **catalogue** de la Petite Maison de l'Épouvante, utilisé comme support **identique** pour comparer deux solutions CI/CD (EPIC 04).

```
app/                      Mini-service (Flask) : /health, /api/produits, calcul TVA
tests/                    Tests unitaires (pytest)
Dockerfile                Image de production (non-root)
ci/smoke-test.sh          Smoke test commun aux deux pipelines
.github/workflows/ci.yml  Pipeline GitHub Actions
Jenkinsfile               Pipeline Jenkins (mêmes étapes)
jenkins/                  Jenkins auto-hébergé, configuré par le code (Docker + JCasC + Job DSL)
demo/scenario.sh          Scénarios pour casser volontairement le pipeline
```

**Pipeline de référence :** secrets (gitleaks) ‖ lint + tests (ruff, pytest ≥ 80 %) ‖ SAST + SCA (bandit, pip-audit) → build de l'image → scan de l'image (trivy) → smoke test → publication (branche `main`).

---

## Prérequis

- Docker Desktop (ou Docker Engine) démarré
- Git
- Un compte GitHub (pour la démo GitHub Actions)

## 0. Initialiser le dépôt de démo

Ce dossier est **un dépôt Git à part entière**, distinct du dépôt de documentation :

```bash
cd demos/cicd
git init -b main
git add -A
git commit -m "Démo CI/CD : mini-service catalogue"
```

---

## 1. Démo GitHub Actions

```bash
# Créer un dépôt vide sur GitHub (par exemple petite-maison-cicd-demo), puis :
git remote add origin https://github.com/<compte>/petite-maison-cicd-demo.git
git push -u origin main
```

1. Ouvrir l'onglet **Actions** du dépôt : le workflow *CI/CD catalogue* démarre automatiquement.
2. Montrer : les **3 jobs parallèles**, puis le job de build, les logs de chaque étape, le **résumé** (tests et image publiée) et l'**artefact** `rapports-tests`.
3. L'image publiée apparaît dans **Packages** (GHCR).
4. Démo d'une PR : créer une branche, ouvrir une pull request. Le statut du pipeline s'affiche **directement sur la PR**.

## 2. Démo Jenkins

```bash
cd jenkins
docker compose up -d --build        # premier lancement : environ 3 à 5 min (téléchargement des plugins)
```

1. Ouvrir http://localhost:8080 et se connecter avec `admin` / `admin` (modifiable via `JENKINS_ADMIN_PASSWORD`).
2. Le job **petite-maison-catalogue** est **déjà créé par le code** (JCasC). Il interroge le dépôt local (`file:///source`) toutes les minutes.
3. Lancer **Build Now** (ou faire un commit : il est détecté en moins d'1 minute).
4. Montrer : la vue des étapes (*Stages* ou *Pipeline Overview*), la branche `parallel`, les **résultats de tests JUnit**, les logs horodatés.
5. L'image est publiée dans le registre local : `curl http://localhost:5000/v2/petite-maison/catalogue/tags/list`

Pour pointer Jenkins vers le dépôt GitHub plutôt que vers le dossier local :
`REPO_URL=https://github.com/<compte>/petite-maison-cicd-demo.git docker compose up -d`

Arrêt : `docker compose down` (ajouter `-v` pour tout réinitialiser).

---

## 3. Scénarios « pipeline rouge »

```bash
sh demo/scenario.sh regression   # TVA passée à 21 % : les tests unitaires échouent
sh demo/scenario.sh secret       # Faux jeton GitHub commité : gitleaks bloque
git commit -am "scénario de démo" && git push     # GitHub ; Jenkins détecte le commit seul
sh demo/scenario.sh reset && git commit -am "retour au vert" && git push
```

Dans les deux cas, **le build, le scan et la publication ne s'exécutent pas** : la quality gate a protégé la livraison.

> ⚠️ **Scénario `secret` sur GitHub :** la *push protection* de GitHub peut refuser le push avant même que le pipeline ne tourne. C'est une **couche de défense supplémentaire** propre à GitHub, à montrer comme telle.

---

## 4. Plan de secours (en cas d'aléa le jour J)

| Aléa | Solution de secours |
|---|---|
| Pas de connexion Internet / GitHub indisponible | Démo Jenkins **100 % locale** (images Docker déjà téléchargées la veille avec `docker compose up` puis un build complet) + **captures d'écran et vidéo** d'un run GitHub Actions |
| Jenkins ne démarre pas | Vidéo enregistrée d'un run complet + captures de la vue des étapes |
| Pipeline trop long en direct | Lancer le run **avant** la présentation, montrer le résultat, puis montrer en direct uniquement un scénario rouge (échec en moins d'1 min) |
| Tout en panne | Exécution manuelle des mêmes commandes en local (cf. section 5) |

À préparer la veille : un build complet sur chaque outil (cache des images), des captures et une vidéo de 1 à 2 min par outil.

## 5. Exécution locale (sans outil CI)

```bash
python -m venv .venv && . .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
ruff check . && pytest --cov=app --cov-fail-under=80 && bandit -r app -lll && pip-audit -r requirements.txt
docker build -t catalogue:local . && sh ci/smoke-test.sh catalogue:local smoke-local
```
