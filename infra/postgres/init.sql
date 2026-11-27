-- Une base et un compte par service : aucun service ne lit les données d'un autre (US-03.2).
CREATE USER catalogue WITH PASSWORD 'catalogue';
CREATE DATABASE catalogue OWNER catalogue;

CREATE USER commandes WITH PASSWORD 'commandes';
CREATE DATABASE commandes OWNER commandes;
