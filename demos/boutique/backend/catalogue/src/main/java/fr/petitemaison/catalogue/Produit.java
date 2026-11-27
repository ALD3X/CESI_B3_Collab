package fr.petitemaison.catalogue;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import java.math.BigDecimal;

@Entity
public class Produit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String nom;

    @Column(nullable = false)
    private String categorie;

    @Column(length = 500)
    private String description;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal prixHt;

    private int stock;

    protected Produit() {
        // requis par JPA
    }

    public Produit(String nom, String categorie, String description, String prixHt, int stock) {
        this.nom = nom;
        this.categorie = categorie;
        this.description = description;
        this.prixHt = new BigDecimal(prixHt);
        this.stock = stock;
    }

    public Long getId() {
        return id;
    }

    public String getNom() {
        return nom;
    }

    public String getCategorie() {
        return categorie;
    }

    public String getDescription() {
        return description;
    }

    public BigDecimal getPrixHt() {
        return prixHt;
    }

    public int getStock() {
        return stock;
    }
}
