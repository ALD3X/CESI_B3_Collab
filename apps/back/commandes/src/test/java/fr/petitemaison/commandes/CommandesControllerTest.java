package fr.petitemaison.commandes;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.cloud.stream.binder.test.EnableTestBinder;
import org.springframework.cloud.stream.binder.test.OutputDestination;
import org.springframework.http.MediaType;
import org.springframework.messaging.Message;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@EnableTestBinder
class CommandesControllerTest {

    @Autowired
    private MockMvc mvc;

    @Autowired
    private OutputDestination bus;

    @MockitoBean
    private CatalogueClient catalogue;

    private static final String CORPS = "{\"lignes\":[{\"produitId\":1,\"quantite\":2}]}";

    @Test
    void commandeEnregistreeEtEvenementPublie() throws Exception {
        when(catalogue.produit(anyLong())).thenReturn(Optional.of(
                new CatalogueClient.ProduitCatalogue(1, "Figurine", new BigDecimal("59.88"), 10)));

        mvc.perform(post("/api/commandes").with(jwt().jwt(j -> j.subject("morticia@petitemaison.fr")))
                        .contentType(MediaType.APPLICATION_JSON).content(CORPS))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.montant").value(119.76))
                .andExpect(jsonPath("$.statut").value("PAYEE"));

        Message<byte[]> evenement = bus.receive(1000, "commandes");
        assertThat(new String(evenement.getPayload(), StandardCharsets.UTF_8))
                .contains("\"membre\":\"morticia@petitemaison.fr\"").contains("\"montant\":119.76");
    }

    @Test
    void sansJetonRefuse() throws Exception {
        mvc.perform(post("/api/commandes").contentType(MediaType.APPLICATION_JSON).content(CORPS))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void produitInconnuRefuse() throws Exception {
        when(catalogue.produit(anyLong())).thenReturn(Optional.empty());
        mvc.perform(post("/api/commandes").with(jwt()).contentType(MediaType.APPLICATION_JSON).content(CORPS))
                .andExpect(status().isBadRequest());
    }

    @Test
    void quantiteHorsLimiteRefusee() throws Exception {
        mvc.perform(post("/api/commandes").with(jwt()).contentType(MediaType.APPLICATION_JSON)
                        .content("{\"lignes\":[{\"produitId\":1,\"quantite\":50}]}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void mesCommandesFiltreesParMembre() throws Exception {
        mvc.perform(get("/api/commandes").with(jwt().jwt(j -> j.subject("inconnu@petitemaison.fr"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void evenementInvalidePublieEnDemo() throws Exception {
        mvc.perform(post("/api/commandes/demo/evenement-invalide").with(jwt()))
                .andExpect(status().isAccepted());
        assertThat(new String(bus.receive(1000, "commandes").getPayload(), StandardCharsets.UTF_8))
                .contains("\"montant\":-5.00");
    }
}
