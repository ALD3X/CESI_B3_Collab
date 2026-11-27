package fr.petitemaison.catalogue;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class CatalogueControllerTest {

    @Autowired
    private MockMvc mvc;

    @Test
    void listeLesProduitsAmorces() throws Exception {
        mvc.perform(get("/api/catalogue/produits")).andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(8));
    }

    @Test
    void detailAvecPrixTtc() throws Exception {
        mvc.perform(get("/api/catalogue/produits/1")).andExpect(status().isOk())
                .andExpect(jsonPath("$.prix_ttc").value(59.88));
    }

    @Test
    void produitInconnu() throws Exception {
        mvc.perform(get("/api/catalogue/produits/999")).andExpect(status().isNotFound());
    }

    @ParameterizedTest
    @CsvSource({"100.00, figurine, 120.00", "4.50, fanzine, 4.59", "0.00, film, 0.00"})
    void tva(String ht, String categorie, String attendu) {
        assertEquals(new BigDecimal(attendu), Tarification.prixTtc(new BigDecimal(ht), categorie));
    }

    @Test
    void prixNegatifRefuse() {
        BigDecimal negatif = new BigDecimal("-1");
        assertThrows(IllegalArgumentException.class, () -> Tarification.prixTtc(negatif, "film"));
    }
}
