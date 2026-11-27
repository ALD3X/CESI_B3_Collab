# PostgreSQL 16 avec le script de création des bases (une base et un compte par service).
FROM postgres:16-alpine
COPY init.sql /docker-entrypoint-initdb.d/init.sql
