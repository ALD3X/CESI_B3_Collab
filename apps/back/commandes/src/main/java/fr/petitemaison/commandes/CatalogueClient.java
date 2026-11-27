package fr.petitemaison.commandes;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.util.Optional;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/** Appel synchrone au service catalogue pour obtenir le prix de référence (jamais celui envoyé par le client). */
@Component
public class CatalogueClient {

    public record ProduitCatalogue(long id, String nom, @JsonProperty("prix_ttc") BigDecimal prixTtc, int stock) {
    }

    private final RestClient client;

    public CatalogueClient(RestClient.Builder builder, @Value("${boutique.catalogue-url}") String url) {
        this.client = builder.baseUrl(url).build();
    }

    public Optional<ProduitCatalogue> produit(long id) {
        return Optional.ofNullable(client.get().uri("/api/catalogue/produits/{id}", id)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, (requete, reponse) -> { })
                .body(ProduitCatalogue.class));
    }
}
