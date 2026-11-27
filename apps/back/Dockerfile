# syntax=docker/dockerfile:1
# Image commune aux services Spring Boot : docker build --build-arg MODULE=commandes -t boutique-commandes apps/back/
# L'étape de build compile TOUS les modules et ne dépend pas de MODULE : elle est identique pour les 6 images,
# donc BuildKit ne l'exécute qu'une fois. Les dépendances ne sont téléchargées qu'une seule fois (6 résolutions
# en parallèle depuis la même machine déclenchaient des refus « 429 Too Many Requests » de Maven Central).
FROM maven:3.9-eclipse-temurin-25 AS build
WORKDIR /src
COPY pom.xml .
COPY contrats/ contrats/
COPY identite/ identite/
COPY catalogue/ catalogue/
COPY commandes/ commandes/
COPY notifications/ notifications/
COPY expedition/ expedition/
COPY passerelle/ passerelle/
RUN --mount=type=cache,target=/root/.m2,sharing=locked mvn -B -ntp package -DskipTests

FROM eclipse-temurin:25-jre
ARG MODULE
WORKDIR /srv
COPY --from=build /src/${MODULE}/target/app.jar app.jar
RUN useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 8080
# La JVM s'adapte à la limite mémoire du conteneur
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75 -XX:+UseSerialGC"
ENTRYPOINT ["java", "-jar", "app.jar"]
