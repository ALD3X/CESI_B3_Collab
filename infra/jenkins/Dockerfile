# Jenkins de démonstration, entièrement configuré par le code (JCasC + Job DSL).
FROM jenkins/jenkins:lts-jdk25

USER root
# Client Docker + Docker Compose : les étapes du pipeline pilotent Docker via le socket de l'hôte.
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:27-cli /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose
# CLI Argo CD : Jenkins ne déploie pas lui-même, il transmet la version des images à Argo CD (GitOps).
# Aucun kubectl ni accès au cluster : seul un jeton Argo CD limité au projet boutique.
RUN curl -fsSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/download/v3.6.3/argocd-linux-amd64 \
    && chmod +x /usr/local/bin/argocd
# Node.js 24.22.3 (LTS) : les étapes du pipeline passent par les scripts du package.json (npm run …)
COPY --from=node:24.22.3-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:24.22.3-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN apt-get update && apt-get install -y --no-install-recommends libatomic1 && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx
RUN git config --system --add safe.directory '*'

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

COPY casc.yaml /usr/share/jenkins/ref/casc.yaml
ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc.yaml \
    JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true"
