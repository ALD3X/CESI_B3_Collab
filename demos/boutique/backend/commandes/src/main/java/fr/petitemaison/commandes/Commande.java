package fr.petitemaison.commandes;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Embeddable;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
public class Commande {

    @Id
    private String id;

    @Column(nullable = false)
    private String membre;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal montant;

    @Column(nullable = false)
    private String statut;

    @Column(nullable = false)
    private Instant creeeLe;

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "ligne_commande")
    private List<Ligne> lignes = new ArrayList<>();

    @Embeddable
    public record Ligne(long produitId, String nom, int quantite, BigDecimal prixUnitaireTtc) {
    }

    protected Commande() {
        // requis par JPA
    }

    public Commande(String membre, List<Ligne> lignes) {
        this.id = "C-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        this.membre = membre;
        this.lignes = new ArrayList<>(lignes);
        this.montant = lignes.stream()
                .map(l -> l.prixUnitaireTtc().multiply(BigDecimal.valueOf(l.quantite())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        // Paiement simulé : dans la plateforme réelle, statut mis à jour par l'adaptateur du prestataire de paiement
        this.statut = "PAYEE";
        this.creeeLe = Instant.now();
    }

    public String getId() {
        return id;
    }

    public String getMembre() {
        return membre;
    }

    public BigDecimal getMontant() {
        return montant;
    }

    public String getStatut() {
        return statut;
    }

    public Instant getCreeeLe() {
        return creeeLe;
    }

    public List<Ligne> getLignes() {
        return List.copyOf(lignes);
    }
}
