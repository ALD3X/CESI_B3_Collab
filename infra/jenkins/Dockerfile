# Jenkins de démonstration, entièrement configuré par le code (JCasC + Job DSL).
FROM jenkins/jenkins:lts-jdk25

USER root
# Client Docker + Docker Compose : les étapes du pipeline pilotent Docker via le socket de l'hôte.
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:27-cli /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose
# kubectl : déploiements accp et prod sur Kubernetes
RUN curl -fsSL -o /usr/local/bin/kubectl https://dl.k8s.io/release/v1.34.1/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl
RUN git config --system --add safe.directory '*'

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

COPY casc.yaml /usr/share/jenkins/ref/casc.yaml
ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc.yaml \
    JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true"
