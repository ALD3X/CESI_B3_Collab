package fr.petitemaison.identite;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class ConnexionControllerTest {

    @Autowired
    private MockMvc mvc;

    private org.springframework.test.web.servlet.ResultActions connexion(String email, String mdp) throws Exception {
        return mvc.perform(post("/api/identite/connexion").contentType(MediaType.APPLICATION_JSON)
                .content("{\"email\":\"" + email + "\",\"motDePasse\":\"" + mdp + "\"}"));
    }

    @Test
    void connexionReussieRenvoieUnJeton() throws Exception {
        connexion("morticia@petitemaison.fr", "Epouvante2026!")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.jeton").isNotEmpty())
                .andExpect(jsonPath("$.nom").value("Morticia"));
    }

    @Test
    void mauvaisMotDePasseRefuse() throws Exception {
        connexion("morticia@petitemaison.fr", "faux").andExpect(status().isUnauthorized());
    }

    @Test
    void compteInconnuRefuseAvecLeMemeMessage() throws Exception {
        connexion("inconnu@petitemaison.fr", "Epouvante2026!")
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.erreur").value("Identifiants invalides"));
    }
}
