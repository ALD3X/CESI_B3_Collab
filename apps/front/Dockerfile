# syntax=docker/dockerfile:1
# Contexte de build : la racine du monorepo (espaces de travail npm, un seul package-lock.json).
# Seuls les fichiers utiles entrent dans le contexte : voir Dockerfile.dockerignore.
FROM node:20-alpine AS build
WORKDIR /src
COPY package.json package-lock.json ./
COPY apps/front/package.json apps/front/
COPY apps/back/package.json apps/back/
RUN --mount=type=cache,target=/root/.npm npm ci --workspace @boutique/front --include-workspace-root=false
COPY apps/front/index.html apps/front/vite.config.js apps/front/
COPY apps/front/src/ apps/front/src/
RUN npm run build --workspace @boutique/front

# NGINX non-root (port 8080) : le fichier de configuration est généré au démarrage depuis le modèle
FROM nginxinc/nginx-unprivileged:1.29-alpine
# Correctifs de sécurité des paquets de l'image de base (ex. CVE-2026-111497 sur brotli, bloquée par le scan)
USER root
RUN apk upgrade --no-cache
USER 101
COPY apps/front/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /src/apps/front/dist /usr/share/nginx/html
ENV PASSERELLE_HOTE=passerelle-spring:8080 PASSERELLE_NOM="Spring Cloud Gateway" BUS=RabbitMQ
EXPOSE 8080
