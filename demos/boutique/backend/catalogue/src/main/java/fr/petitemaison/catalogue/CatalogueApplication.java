package fr.petitemaison.catalogue;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class CatalogueApplication {

    public static void main(String[] args) {
        SpringApplication.run(CatalogueApplication.class, args);
    }

    /** Jeu de données de démonstration, inséré seulement si le catalogue est vide. */
    @Bean
    CommandLineRunner amorcage(ProduitRepository produits) {
        return args -> {
            if (produits.count() > 0) {
                return;
            }
            produits.save(new Produit("Figurine L'Orc (exclusivité Evil Ed)", "figurine",
                    "Résine peinte à la main, 25 cm, série limitée à 300 exemplaires.", "49.90", 12));
            produits.save(new Produit("Fanzine n°38 (numérique)", "fanzine",
                    "Dossier « Les maisons hantées du cinéma italien », lisible dans la liseuse.", "4.50", 999));
            produits.save(new Produit("Blu-ray Riflesso di un coltello nella notte", "film",
                    "Giallo restauré en 4K, version originale sous-titrée.", "24.99", 30));
            produits.save(new Produit("Affiche sérigraphiée La Nuit des Taupes Mutantes", "affiche",
                    "Sérigraphie 3 couleurs, 50 x 70 cm, signée par l'illustratrice.", "35.00", 8));
            produits.save(new Produit("Masque en latex Le Vampire de Vesoul", "masque",
                    "Latex naturel, cheveux synthétiques, taille unique.", "39.90", 15));
            produits.save(new Produit("Coffret DVD La Trilogie du Grenier", "film",
                    "Trois films, bonus inédits et livret de 40 pages.", "44.99", 20));
            produits.save(new Produit("Figurine La Nonne aux Corbeaux", "figurine",
                    "Résine et socle en bois flotté, 30 cm.", "64.90", 5));
            produits.save(new Produit("Fanzine n°37 (papier)", "fanzine",
                    "Spécial festival : entretiens et programme commenté.", "6.00", 120));
        };
    }
}
