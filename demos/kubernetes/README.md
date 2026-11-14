# Démo EPIC 06 : architecture interne de Kubernetes

Cluster local **minikube à 2 nœuds** (1 control plane + 1 worker) sur lequel on déploie le mini-service catalogue de la démo CI/CD. Le but est de **voir fonctionner** les composants décrits dans [US-06.1](../../docs/environnement_tests/US-06.1_architecture_orchestrateur.md).

```
catalogue.yaml   Namespace, Deployment (2 instances, sondes, non-root), Service, HPA, PDB, NetworkPolicy
demo.sh          Étapes de la démo : preparer | composants | deployer | auto-reparation | mise-a-jour | nettoyer
```

Le profil minikube `petite-maison` est **distinct** du profil par défaut : la démo ne touche pas à un autre cluster.

## Déroulé (environ 3 min)

```bash
sh demo.sh preparer          # la veille ou avant la soutenance : ~2 min
sh demo.sh composants        # nœuds + composants du control plane visibles en direct
sh demo.sh deployer          # apply → API server → etcd → scheduler → kubelet
sh demo.sh auto-reparation   # on supprime une instance : elle est recréée (~7 s mesurées)
sh demo.sh mise-a-jour       # passage à 4 instances puis redémarrage progressif sans coupure (~30 s)
sh demo.sh cloisonnement     # NetworkPolicy : accès autorisé depuis la zone, bloqué depuis l'extérieur
sh demo.sh nettoyer
```

| Étape | Composant mis en évidence |
|---|---|
| `composants` | `kube-apiserver`, `etcd`, `kube-scheduler`, `kube-controller-manager` sur le control plane. `kube-proxy` et le plugin réseau sur **chaque** nœud. `coredns` |
| `deployer` | L'**API server** valide et enregistre l'état souhaité dans **etcd**. Le **scheduler** répartit les 2 instances sur les 2 nœuds. Le **kubelet** de chaque nœud démarre les conteneurs (containerd) |
| `auto-reparation` | Le **controller manager** (contrôleur ReplicaSet) détecte 1 instance au lieu de 2 et en recrée une. La **sonde de disponibilité** retient le trafic tant qu'elle n'est pas prête |
| `mise-a-jour` | Mise à jour **progressive** (`maxUnavailable: 0`) : aucune coupure |

## Plan de secours

| Aléa | Solution |
|---|---|
| minikube ne démarre pas | Captures et vidéo de la démo enregistrées la veille. Le schéma US-06.1 suffit à couvrir le critère |
| Machine lente | Ne garder que `composants` et `auto-reparation` (1 min 30) |

> **Cloisonnement vérifié :** la NetworkPolicy est appliquée par le plugin réseau de minikube (kindnet). Un appel depuis la zone applicative obtient la réponse du catalogue, alors qu'un appel depuis le namespace `default` est **bloqué** (délai dépassé). Étape `sh demo.sh cloisonnement`.
