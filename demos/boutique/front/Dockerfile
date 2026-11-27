# syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /src
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY index.html vite.config.js ./
COPY src/ src/
RUN npm run build

# NGINX non-root (port 8080) : le fichier de configuration est généré au démarrage depuis le modèle
FROM nginxinc/nginx-unprivileged:1.29-alpine
# Correctifs de sécurité des paquets de l'image de base (ex. CVE-2026-111497 sur brotli, bloquée par le scan)
USER root
RUN apk upgrade --no-cache
USER 101
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /src/dist /usr/share/nginx/html
ENV PASSERELLE_HOTE=passerelle-spring:8080 PASSERELLE_NOM="Spring Cloud Gateway" BUS=RabbitMQ
EXPOSE 8080
