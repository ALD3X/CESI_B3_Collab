package fr.petitemaison.notifications;

import fr.petitemaison.contrats.CommandePayee;
import java.io.IOException;
import java.text.NumberFormat;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/**
 * Consomme « commande payée » et pousse une notification en direct aux navigateurs (Server-Sent Events).
 * Un événement invalide lève une exception : après 3 tentatives, le binder l'envoie en rebut (DLQ).
 */
@RestController
@RequestMapping("/api/notifications")
public class NotificationsService {

    private static final Logger LOG = LoggerFactory.getLogger(NotificationsService.class);

    public record Notification(String commandeId, String membre, String message, Instant recueLe) {
    }

    private final List<SseEmitter> abonnes = new CopyOnWriteArrayList<>();
    private final Deque<Notification> dernieres = new ConcurrentLinkedDeque<>();
    private final AtomicInteger recues = new AtomicInteger();
    private final AtomicInteger tentativesRejetees = new AtomicInteger();
    private final String bus;

    public NotificationsService(@Value("${spring.cloud.stream.default-binder}") String bus) {
        this.bus = bus;
    }

    @Bean
    public Consumer<CommandePayee> commandePayee() {
        return evenement -> {
            if (!evenement.estValide()) {
                tentativesRejetees.incrementAndGet();
                throw new IllegalArgumentException("Événement invalide : " + evenement.commandeId());
            }
            String montant = NumberFormat.getCurrencyInstance(Locale.FRANCE).format(evenement.montant());
            Notification n = new Notification(evenement.commandeId(), evenement.membre(),
                    "Commande " + evenement.commandeId() + " payée (" + montant + "). Merci !", Instant.now());
            recues.incrementAndGet();
            dernieres.addFirst(n);
            while (dernieres.size() > 20) {
                dernieres.removeLast();
            }
            diffuser("notification", n);
        };
    }

    @GetMapping(path = "/flux", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter flux() {
        SseEmitter emetteur = new SseEmitter(30 * 60 * 1000L);
        abonnes.add(emetteur);
        emetteur.onCompletion(() -> abonnes.remove(emetteur));
        emetteur.onTimeout(() -> abonnes.remove(emetteur));
        emetteur.onError(e -> abonnes.remove(emetteur));
        return emetteur;
    }

    @GetMapping("/stats")
    public Map<String, Object> stats() {
        return Map.of("service", "notifications", "bus", bus, "recues", recues.get(),
                "tentativesRejetees", tentativesRejetees.get(), "abonnesEnDirect", abonnes.size(),
                "dernieres", new ArrayList<>(dernieres));
    }

    /** Battement toutes les 20 s : garde les connexions ouvertes à travers les proxys et la passerelle. */
    @Scheduled(fixedRate = 20_000)
    void battement() {
        diffuser("battement", "");
    }

    private void diffuser(String type, Object donnees) {
        for (SseEmitter emetteur : abonnes) {
            try {
                emetteur.send(SseEmitter.event().name(type).data(donnees));
            } catch (IOException | IllegalStateException e) {
                LOG.debug("Abonné déconnecté : {}", e.getMessage());
                abonnes.remove(emetteur);
            }
        }
    }
}
