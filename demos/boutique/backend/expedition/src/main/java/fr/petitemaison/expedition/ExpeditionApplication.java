package fr.petitemaison.expedition;

import fr.petitemaison.contrats.CommandePayee;
import java.util.ArrayList;
import java.util.Deque;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Consommateur de « commande payée ». Le nom et le groupe de consommateurs sont paramétrables :
 * la même image joue « expédition » et, pour la démo de rejeu, un nouveau service « recommandations ».
 */
@SpringBootApplication
@RestController
public class ExpeditionApplication {

    private final AtomicInteger recues = new AtomicInteger();
    private final AtomicInteger tentativesRejetees = new AtomicInteger();
    private final Deque<String> dernieres = new ConcurrentLinkedDeque<>();
    private final String nom;
    private final String groupe;
    private final String bus;

    public ExpeditionApplication(@Value("${boutique.service}") String nom,
                                 @Value("${spring.cloud.stream.bindings.commandePayee-in-0.group}") String groupe,
                                 @Value("${spring.cloud.stream.default-binder}") String bus) {
        this.nom = nom;
        this.groupe = groupe;
        this.bus = bus;
    }

    public static void main(String[] args) {
        SpringApplication.run(ExpeditionApplication.class, args);
    }

    @Bean
    public Consumer<CommandePayee> commandePayee() {
        return evenement -> {
            if (!evenement.estValide()) {
                tentativesRejetees.incrementAndGet();
                throw new IllegalArgumentException("Événement invalide : " + evenement.commandeId());
            }
            recues.incrementAndGet();
            dernieres.addFirst(evenement.commandeId());
            while (dernieres.size() > 20) {
                dernieres.removeLast();
            }
        };
    }

    @GetMapping("/api/{service}/stats")
    public Map<String, Object> stats() {
        return Map.of("service", nom, "groupe", groupe, "bus", bus, "recues", recues.get(),
                "tentativesRejetees", tentativesRejetees.get(), "dernieres", new ArrayList<>(dernieres));
    }
}
