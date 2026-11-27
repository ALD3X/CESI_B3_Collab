#!/bin/sh
# Donne au Jenkins de démonstration l'accès au cluster minikube (environnements accp et prod).
# À lancer après « docker compose up -d » et « sh k8s/demo.sh preparer ».
#   1. Jenkins rejoint le réseau Docker du cluster ;
#   2. un fichier kubeconfig pointant vers l'adresse interne du cluster lui est copié.
set -eu
PROFIL="${1:-boutique}"
CONTENEUR="boutique-jenkins-jenkins-1"
cd "$(dirname "$0")"

docker network connect "$PROFIL" "$CONTENEUR" 2>/dev/null || echo "Jenkins est déjà sur le réseau $PROFIL."
IP=$(minikube -p "$PROFIL" ip)
kubectl config view --raw --minify --flatten --context "$PROFIL" \
  | sed -E "s#server: https://[^ ]+#server: https://$IP:8443#" > /tmp/kubeconfig-jenkins
docker exec "$CONTENEUR" mkdir -p /var/jenkins_home/.kube
docker cp /tmp/kubeconfig-jenkins "$CONTENEUR:/var/jenkins_home/.kube/config"
rm -f /tmp/kubeconfig-jenkins
docker exec "$CONTENEUR" kubectl --kubeconfig /var/jenkins_home/.kube/config get nodes
echo "Jenkins peut déployer sur le cluster « $PROFIL »."
