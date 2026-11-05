# Jenkins de démonstration, entièrement configuré par le code (JCasC + Job DSL).
FROM jenkins/jenkins:lts-jdk17

USER root
# Client Docker : les étapes du pipeline lancent des conteneurs via le socket de l'hôte.
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
RUN git config --system --add safe.directory '*'

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

COPY casc.yaml /usr/share/jenkins/ref/casc.yaml
ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc.yaml \
    JAVA_OPTS="-Djenkins.install.runSetupWizard=false -Dhudson.plugins.git.GitSCM.ALLOW_LOCAL_CHECKOUT=true"
