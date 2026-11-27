# Conclusion comparative CI/CD

> **Story :** US-04.4 · **Jira :** [SCRUM-26](https://maalsi25.atlassian.net/browse/SCRUM-26) · **Epic :** EPIC 04, Comparaison et démonstration de deux solutions CI/CD
> **Responsable :** Membre B · **Binôme :** Membre D
> **Entrées :** [US-04.1, critères](candidats-et-criteres.md) · [US-04.2, démo GitHub Actions](demo-github-actions.md) · [US-04.3, démo Jenkins + Argo CD](demo-jenkins-argocd.md)

---

## 1. Ce que les démonstrations montrent

| Observation | GitHub Actions | Jenkins + Argo CD | Source |
|---|---|---|---|
| **Mise en place** | Des fichiers YAML suffisent, aucun serveur | Image Jenkins, plugins, JCasC et Job DSL, **puis** installation et configuration d'Argo CD dans le cluster | US-04.2 §2, US-04.3 §6 n°1 |
| **Même scénario de CI** | Contrôles en parallèle, images, scan, test de bout en bout | Mêmes étapes, mêmes scripts npm | US-04.1 §3 |
| **Modèle de déploiement** | **Push** : le pipeline applique les manifestes avec `kubectl` | **Pull** : Argo CD, dans le cluster, applique l'état décrit dans Git | US-04.3 §1 |
| **Accès au cluster depuis la CI** | Nécessaire : `KUBECONFIG` dans les secrets de l'environnement GitHub | **Aucun** : un jeton Argo CD limité au projet `boutique` | US-04.3 §2 |
| **Écart entre le cluster et Git** | Non détecté entre deux exécutions du pipeline | **Détecté** en permanence, et **corrigé automatiquement** en recette (*selfHeal*) | US-04.3 §4 n°3 |
| **Retour arrière en production** | Script (`kubectl rollout undo`) | Historique des synchronisations d'Argo CD | US-04.3 §5 |
| **Visibilité de ce qui est déployé** | Historique des déploiements des environnements GitHub | **Arbre des ressources** en direct, version et état de santé dans l'interface d'Argo CD | US-04.3 §4 n°2 |
| **Détection d'une régression ou d'un secret** | Job rouge, statut rouge sur la PR, rien n'est publié | Étape rouge, tests en échec affichés, rien n'est publié | US-04.2 §4, US-04.3 §5 |
| **Chaîne dev → accp → prod** | Environnements GitHub, ruleset (pull requests obligatoires), approbation native de la production | Job multi-branches, étape `input` d'approbation, synchronisation manuelle de la production | [US-04.5](branches-et-environnements.md) |
| **Déclenchement** | Webhook natif : quelques secondes | Polling Jenkins : jusqu'à 1 min ; Argo CD compare le cluster à Git toutes les 60 s | US-04.3 §6 n°6 |
| **Ressources consommées** | Rien sur notre infrastructure | Serveur Jenkins, plus les composants d'Argo CD dans le cluster (nœuds locaux agrandis pour la démo) | US-04.3 §6 n°3 |

---

## 2. Forces, faiblesses et limites

### GitHub Actions

| Forces | Faiblesses | Limites |
|---|---|---|
| Aucune infrastructure à maintenir | Code, logs et artefacts traités **par défaut aux États-Unis** | **Dépendance forte** à GitHub (forge + CI + registre) |
| Intégration native avec les PR, le registre GHCR et les jetons éphémères | Le pipeline doit **détenir les accès au cluster** pour déployer | Rien ne surveille le cluster entre deux exécutions : un changement manuel passe inaperçu |
| Runner neuf à chaque job : isolation forte | Actions tierces = risque de **chaîne d'approvisionnement** | **Quotas** de minutes sur les dépôts privés |
| Moindre privilège simple (`permissions:` par job), approbation native de la production | Débogage : pas d'exécution locale native | Runners auto-hébergés possibles, mais réintroduisent la maintenance |

### Jenkins + Argo CD

| Forces | Faiblesses | Limites |
|---|---|---|
| **Hébergé où l'on veut** (cloud européen) : souveraineté totale de toute la chaîne | **Deux outils** à installer, sécuriser et maintenir | **Doit être exploité comme un service de production** : disponibilité, sauvegardes, mises à jour |
| **GitOps** : Git est la référence, tout écart est visible et corrigé | **Plugins Jenkins = dette** : mises à jour fréquentes, alertes de sécurité | Serveur Jenkins = **cible de valeur** pour un attaquant (code, secrets) |
| **La CI n'a aucun accès au cluster** : seul Argo CD, à l'intérieur, déploie | Composants d'Argo CD à faire tenir dans le cluster | Dans la démo, la version des images est transmise en paramètre : l'état déployé n'est pas entièrement dans Git (corrigé en production par *Argo CD Image Updater*) |
| Interface Argo CD : état déployé, santé et historique en direct ; retour arrière en un geste | Durcissement de Jenkins à notre charge (socket Docker, accès) | Charge humaine : environ 15 à 25 % d'un ETP DevOps pour les deux outils |
| Approbation (`input`) native et gratuite, fonctionne hors forge | | |

---

## 3. Notation pondérée

Notes de 1 (faible) à 5 (excellent). Les poids sont définis dans [US-04.1](candidats-et-criteres.md) §2.

| Critère | Poids | GitHub Actions | Jenkins + Argo CD | Justification |
|---|---|---|---|---|
| K1 Simplicité de mise en place | ×3 | **5** | 2 | Des YAML contre deux outils à installer et à relier |
| K2 Intégration au dépôt | ×2 | **5** | 3 | Statut PR natif contre webhook et plugins à configurer |
| K3 Sécurité de la chaîne CI/CD | ×3 | 4 | 4 | GitHub : runners et jetons éphémères, mais accès au cluster dans la CI. Jenkins + Argo CD : aucun accès au cluster dans la CI, mais un serveur Jenkins à durcir |
| K4 Maintenance | ×3 | **5** | 1 | Rien à maintenir contre deux services à exploiter |
| K5 Souveraineté et hébergement | ×2 | 2 | **5** | Exécutions aux États-Unis par défaut contre hébergement libre dans l'UE |
| K6 Coût | ×2 | **4** | 3 | Gratuit dans les quotas contre licences gratuites mais infrastructure et temps humain |
| K7 Richesse et extensibilité | ×1 | 4 | **5** | Marketplace riche contre plugins Jenkins et écosystème Argo CD |
| K8 Observabilité | ×1 | 4 | **5** | Résumés des runs contre Stage View, tendances des tests et arbre des ressources déployées |
| K9 Fiabilité du déploiement | ×2 | 3 | **5** | Déploiement ponctuel par script contre réconciliation permanente, correction des écarts et historique |
| **Total (sur 95)** | | **78** | **63** | |

**Analyse de sensibilité :** en portant le poids de la souveraineté (K5) à ×5, l'écart se resserre (**84** contre **78**) sans s'inverser. Le classement ne s'inverse que si l'**hébergement UE de toute la chaîne** devient une **exigence bloquante**.

---

## 4. Recommandation pour la Petite Maison de l'Épouvante

### Recommandation : GitHub Actions pour la CI, avec trois conditions

**Pourquoi, dans ce contexte précis :**
- L'équipe (1 architecte, 2 alternants, un DevOps à recruter d'après US-02.3) **ne peut pas absorber l'exploitation de Jenkins** en plus du développement de la plateforme (contrainte C-11).
- À **scénario identique**, GitHub Actions offre **les mêmes quality gates** pour un coût de mise en place et de maintenance bien plus faible.

**Conditions :**
1. **Déploiement en GitOps (C-03, C-04) :** la démo montre que la vraie valeur de la seconde chaîne est **Argo CD**, pas Jenkins. Dès que le cluster managé européen est en place, le déploiement est confié à **Argo CD, installé dans ce cluster** : GitHub Actions publie les images, Argo CD les déploie. GitHub ne détient alors **aucun accès** au cluster de production, et tout écart avec Git est corrigé.
2. **Chaîne d'approvisionnement (C-03) :** actions tierces **figées par SHA**, liste d'actions autorisées, Dependabot activé sur les workflows.
3. **Réversibilité :** les étapes restent des **scripts npm standards** (`package.json`), pour pouvoir changer de CI sans réécrire la logique. La démo l'a prouvé : le même scénario tourne sur les deux chaînes.

### Quand Jenkins + Argo CD redeviendrait le bon choix

Cette recommandation **n'est pas universelle**. La chaîne entièrement auto-hébergée serait préférable si :
- l'hébergement **UE de toute la chaîne** devient une **obligation** (contrat, client public, données sensibles dans les tests) ;
- l'équipe DevOps grandit et peut **exploiter les deux outils de façon professionnelle** ;
- des besoins spécifiques apparaissent : pipelines très longs (vidéo Evil Ed en V2), matériel particulier, exécution hors réseau.

> **Message pour la soutenance :** *« Les deux chaînes savent faire le travail : nous l'avons démontré sur le même scénario. Pour l'intégration continue, une petite équipe gagne à ne pas exploiter son propre serveur : GitHub Actions. Pour le déploiement, Argo CD nous a convaincus : la production ne dépend plus d'un pipeline qui détient ses accès, elle se compare en permanence à Git et se corrige seule. Nous retenons donc GitHub Actions pour la CI, et Argo CD pour le déploiement dès que le cluster européen est en place. »*

---

[← Démonstration du second outil : Jenkins + Argo CD](demo-jenkins-argocd.md) · [Sommaire](../README.md) · [Branches, environnements et chaîne de livraison (dev → accp → prod) →](branches-et-environnements.md)
