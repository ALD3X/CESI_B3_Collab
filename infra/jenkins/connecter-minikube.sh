#!/bin/sh
# Relie le Jenkins de démonstration au cluster minikube.
#   npm run jenkins:connecter   (après « npm run jenkins:demarrer » et « npm run k8s -- preparer »)
# Jenkins rejoint le réseau Docker du cluster pour joindre le serveur Argo CD et le front exposé par les nœuds
# (test de fumée). Il ne reçoit AUCUN accès au cluster Kubernetes : le déploiement passe par Argo CD, avec un
# jeton limité au projet boutique (créé par « npm run argocd:installer »).
set -eu
PROFIL="${1:-boutique}"
CONTENEUR="boutique-jenkins-jenkins-1"

docker network connect "$PROFIL" "$CONTENEUR" 2>/dev/null || echo "Jenkins est déjà sur le réseau $PROFIL."
docker exec "$CONTENEUR" rm -rf /var/jenkins_home/.kube   # ancien accès direct au cluster, plus utilisé
if docker exec "$CONTENEUR" test -f /var/jenkins_home/argocd.env; then
  echo "Jenkins est relié au cluster « $PROFIL » et dispose de son jeton Argo CD."
else
  echo "Jenkins est relié au cluster « $PROFIL ». Jeton Argo CD absent : lancer « npm run argocd:installer »."
fi
