package fr.petitemaison.passerelle;

import java.time.Duration;
import java.util.Map;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.gateway.config.HttpClientCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class PasserelleApplication {

    public static void main(String[] args) {
        SpringApplication.run(PasserelleApplication.class, args);
    }

    /**
     * Cache DNS court : par défaut, le client HTTP garde l'adresse IP d'un service pendant la durée
     * annoncée par le DNS. Constaté : après le redéploiement d'un service (nouvelle IP), la passerelle
     * continuait d'appeler l'ancienne adresse et renvoyait des erreurs 500.
     */
    @Bean
    HttpClientCustomizer cacheDnsCourt() {
        return client -> client.resolver(spec -> spec
                .cacheMaxTimeToLive(Duration.ofSeconds(5))
                .cacheNegativeTimeToLive(Duration.ofSeconds(1))
                // service arrêté : la réponse DNS négative tardait jusqu'à 4 s (constaté)
                .queryTimeout(Duration.ofSeconds(1)));
    }

    /** Réponse de repli du coupe-circuit : une erreur propre plutôt qu'une erreur technique brute. */
    @RequestMapping("/indisponible")
    public ResponseEntity<Map<String, String>> indisponible() {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(Map.of("erreur", "Service momentanément indisponible, réessayez dans quelques instants"));
    }
}
