package fr.petitemaison.expedition;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.cloud.stream.binder.test.EnableTestBinder;
import org.springframework.cloud.stream.binder.test.InputDestination;
import org.springframework.messaging.support.MessageBuilder;

@SpringBootTest
@EnableTestBinder
class ExpeditionApplicationTest {

    @Autowired
    private InputDestination bus;

    @Autowired
    private ExpeditionApplication service;

    @Test
    void commandeValideRecue() {
        String json = "{\"version\":1,\"commandeId\":\"C-EXP\",\"membre\":\"vincent@petitemaison.fr\","
                + "\"montant\":24.99,\"lignes\":[],\"payeeLe\":\"2026-11-27T10:00:00Z\"}";
        bus.send(MessageBuilder.withPayload(json.getBytes(StandardCharsets.UTF_8))
                .setHeader("contentType", "application/json").build(), "commandes");
        assertThat(service.stats().get("recues")).isEqualTo(1);
        assertThat(service.stats().get("service")).isEqualTo("expedition");
    }
}
