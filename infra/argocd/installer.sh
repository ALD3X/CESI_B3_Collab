#!/bin/sh
# Installe Argo CD dans le cluster local (minikube, profil « boutique ») et le relie à Jenkins.
#   npm run argocd:installer   (après « npm run k8s -- preparer » et « npm run jenkins:demarrer »)
#
# 1. Argo CD (version figée) dans le namespace argocd
# 2. Configuration : compte technique « jenkins », droits limités au projet boutique
# 3. Projet et applications : boutique-accp (synchronisation automatique), boutique-prod (manuelle)
# 4. Jeton d'API du compte jenkins, transmis au conteneur Jenkins (fichier /var/jenkins_home/argocd.env)
set -eu
cd "$(dirname "$0")"

VERSION_ARGOCD="v3.6.3"
PROFIL="${PROFIL:-boutique}"
K="kubectl --context $PROFIL"
JENKINS="${JENKINS_CONTENEUR:-boutique-jenkins-jenkins-1}"

echo "== 1. Installation d'Argo CD $VERSION_ARGOCD"
$K create namespace argocd --dry-run=client -o yaml | $K apply -f - >/dev/null
$K apply -n argocd --server-side --force-conflicts \
  -f "https://raw.githubusercontent.com/argoproj/argo-cd/$VERSION_ARGOCD/manifests/install.yaml" >/dev/null
$K -n argocd rollout status deploy/argocd-server --timeout=300s
$K -n argocd rollout status deploy/argocd-repo-server --timeout=300s
$K -n argocd rollout status statefulset/argocd-application-controller --timeout=300s

echo "== 2. Configuration : compte jenkins et droits"
$K -n argocd patch configmap argocd-cm --type merge --patch-file argocd-cm.yaml >/dev/null
$K -n argocd patch configmap argocd-rbac-cm --type merge --patch-file argocd-rbac-cm.yaml >/dev/null
# Serveur Argo CD joignable depuis le réseau du cluster (Jenkins y est connecté)
$K -n argocd patch service argocd-server --type merge -p '{"spec":{"type":"NodePort"}}' >/dev/null
PORT=$($K -n argocd get service argocd-server -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}')
SERVEUR="$(minikube -p "$PROFIL" ip):$PORT"

echo "== 3. Projet et applications"
$K apply -f projet.yaml -f applications.yaml

echo "== 4. Jeton d'API de Jenkins"
MDP=$($K -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)
JETON=$(docker run --rm --network "$PROFIL" "quay.io/argoproj/argocd:$VERSION_ARGOCD" sh -c \
  "argocd login $SERVEUR --username admin --password '$MDP' --insecure --grpc-web >/dev/null \
   && argocd account generate-token --account jenkins --insecure --grpc-web")
if docker inspect "$JENKINS" >/dev/null 2>&1; then
  printf 'ARGOCD_SERVER=%s\nARGOCD_AUTH_TOKEN=%s\n' "$SERVEUR" "$JETON" \
    | docker exec -i "$JENKINS" sh -c 'cat > /var/jenkins_home/argocd.env && chmod 600 /var/jenkins_home/argocd.env'
  echo "Jeton transmis à Jenkins ($JENKINS)."
else
  echo "Jenkins n'est pas démarré : relancer ce script après « npm run jenkins:demarrer »."
fi

echo
echo "Argo CD prêt. Interface : npm run argocd:ouvrir, puis https://localhost:8443 (admin / $MDP)"
