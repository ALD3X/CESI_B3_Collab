package fr.petitemaison.contrats;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

/**
 * Événement métier « commande payée », publié par le service commandes sur le bus
 * (destination « commandes ») et consommé par notifications, expédition, recommandations.
 *
 * <p>Contrat versionné : tout changement incompatible crée une version 2, publiée en parallèle
 * le temps que les consommateurs migrent. C'est ce qui permet de changer de broker sans
 * réécrire les services (condition n°4 de US-05.4).
 */
public record CommandePayee(
        int version,
        String commandeId,
        String membre,
        BigDecimal montant,
        List<Ligne> lignes,
        Instant payeeLe) {

    public static final int VERSION = 1;

    public record Ligne(long produitId, String nom, int quantite) {
    }

    /** Règle de validation commune à tous les consommateurs : un événement invalide part en rebut (DLQ). */
    public boolean estValide() {
        return version == VERSION
                && commandeId != null && !commandeId.isBlank()
                && membre != null && !membre.isBlank()
                && montant != null && montant.signum() > 0;
    }
}
