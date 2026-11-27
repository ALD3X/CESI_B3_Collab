package fr.petitemaison.catalogue;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/catalogue/produits")
public class CatalogueController {

    public record ProduitVue(long id, String nom, String categorie, String description,
                             @JsonProperty("prix_ht") BigDecimal prixHt,
                             @JsonProperty("prix_ttc") BigDecimal prixTtc,
                             int stock) {

        static ProduitVue de(Produit p) {
            return new ProduitVue(p.getId(), p.getNom(), p.getCategorie(), p.getDescription(), p.getPrixHt(),
                    Tarification.prixTtc(p.getPrixHt(), p.getCategorie()), p.getStock());
        }
    }

    private final ProduitRepository produits;

    public CatalogueController(ProduitRepository produits) {
        this.produits = produits;
    }

    @GetMapping
    public List<ProduitVue> lister() {
        return produits.findAll().stream().map(ProduitVue::de).toList();
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProduitVue> detail(@PathVariable long id) {
        return ResponseEntity.of(produits.findById(id).map(ProduitVue::de));
    }
}
