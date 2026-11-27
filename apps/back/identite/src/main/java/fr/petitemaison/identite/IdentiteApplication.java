package fr.petitemaison.identite;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Service d'identité simplifié (composant EN-3 de l'architecture).
 * En production, ce rôle est tenu par un serveur d'identité (OIDC, MFA, jetons RS256).
 */
@SpringBootApplication
public class IdentiteApplication {

    public static void main(String[] args) {
        SpringApplication.run(IdentiteApplication.class, args);
    }
}
