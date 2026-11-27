package fr.petitemaison.passerelle;

import java.nio.charset.StandardCharsets;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusReactiveJwtDecoder;
import org.springframework.security.oauth2.jwt.ReactiveJwtDecoder;
import org.springframework.security.web.server.SecurityWebFilterChain;

@Configuration
@EnableWebFluxSecurity
public class SecuriteConfig {

    @Bean
    SecurityWebFilterChain filtres(ServerHttpSecurity http) {
        return http
                // API sans session ni cookie : le jeton circule dans l'en-tête Authorization
                .csrf(ServerHttpSecurity.CsrfSpec::disable)
                .authorizeExchange(regles -> regles
                        .pathMatchers("/api/identite/**", "/api/catalogue/**", "/api/notifications/**",
                                "/api/expedition/**", "/indisponible", "/actuator/health/**").permitAll()
                        .pathMatchers("/api/commandes/**").authenticated()
                        .anyExchange().denyAll())
                .oauth2ResourceServer(serveur -> serveur.jwt(Customizer.withDefaults()))
                .build();
    }

    /** Signature HS256, expiration et émetteur vérifiés (mêmes contrôles que le plugin jwt de Kong). */
    @Bean
    ReactiveJwtDecoder decodeurJwt(@Value("${passerelle.jwt.secret}") String secret,
                                   @Value("${passerelle.jwt.emetteur}") String emetteur) {
        SecretKey cle = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        NimbusReactiveJwtDecoder decodeur = NimbusReactiveJwtDecoder.withSecretKey(cle)
                .macAlgorithm(MacAlgorithm.HS256).build();
        decodeur.setJwtValidator(JwtValidators.createDefaultWithIssuer(emetteur));
        return decodeur;
    }
}
