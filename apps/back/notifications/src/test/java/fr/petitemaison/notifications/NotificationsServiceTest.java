package fr.petitemaison.notifications;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.cloud.stream.binder.test.EnableTestBinder;
import org.springframework.cloud.stream.binder.test.InputDestination;
import org.springframework.messaging.support.MessageBuilder;

@SpringBootTest
@EnableTestBinder
class NotificationsServiceTest {

    @Autowired
    private InputDestination bus;

    @Autowired
    private NotificationsService service;

    private void publier(String montant) {
        String json = "{\"version\":1,\"commandeId\":\"C-TEST\",\"membre\":\"morticia@petitemaison.fr\","
                + "\"montant\":" + montant + ",\"lignes\":[],\"payeeLe\":\"2026-11-27T10:00:00Z\"}";
        bus.send(MessageBuilder.withPayload(json.getBytes(StandardCharsets.UTF_8))
                .setHeader("contentType", "application/json").build(), "commandes");
    }

    @Test
    void commandeValideNotifiee() {
        int avant = (int) service.stats().get("recues");
        publier("59.88");
        Map<String, Object> stats = service.stats();
        assertThat(stats.get("recues")).isEqualTo(avant + 1);
    }

    @Test
    void abonneEnDirectRecoitLesNotifications() {
        int avant = (int) service.stats().get("abonnesEnDirect");
        service.flux();
        assertThat((int) service.stats().get("abonnesEnDirect")).isEqualTo(avant + 1);
        service.battement();          // le battement ne doit pas couper l'abonnement
        publier("24.99");             // diffusion à l'abonné ouvert
        assertThat(service.stats().get("dernieres").toString()).contains("C-TEST");
    }

    @Test
    void evenementInvalideRejete() {
        int avant = (int) service.stats().get("tentativesRejetees");
        try {
            publier("-5");
        } catch (RuntimeException attendu) {
            // le binder de test propage l'exception après les tentatives
        }
        assertThat((int) service.stats().get("tentativesRejetees")).isGreaterThan(avant);
    }
}
