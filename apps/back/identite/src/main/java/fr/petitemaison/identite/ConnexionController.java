package fr.petitemaison.identite;

import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.security.oauth2.jwt.NimbusJwtEncoder;
import com.nimbusds.jose.jwk.source.ImmutableSecret;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/identite")
public class ConnexionController {

    static final Duration DUREE_JETON = Duration.ofHours(1);

    public record Identifiants(String email, String motDePasse) {
    }

    public record Session(String jeton, String membre, String nom, long expireDans) {
    }

    private record Compte(String nom, String empreinte) {
    }

    private final BCryptPasswordEncoder hachage = new BCryptPasswordEncoder();
    private final Map<String, Compte> comptes;
    private final JwtEncoder encodeur;
    private final String emetteur;

    public ConnexionController(@Value("${boutique.jwt.secret}") String secret,
                               @Value("${boutique.jwt.emetteur}") String emetteur,
                               @Value("${boutique.demo.mot-de-passe}") String motDePasseDemo) {
        this.emetteur = emetteur;
        this.encodeur = new NimbusJwtEncoder(new ImmutableSecret<>(
                new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256")));
        // Comptes de démonstration : mots de passe stockés uniquement sous forme d'empreinte BCrypt
        String empreinte = hachage.encode(motDePasseDemo);
        this.comptes = Map.of(
                "morticia@petitemaison.fr", new Compte("Morticia", empreinte),
                "vincent@petitemaison.fr", new Compte("Vincent", empreinte),
                "elvira@petitemaison.fr", new Compte("Elvira", empreinte));
    }

    @PostMapping("/connexion")
    public ResponseEntity<?> connexion(@RequestBody Identifiants identifiants) {
        Compte compte = identifiants.email() == null ? null : comptes.get(identifiants.email().toLowerCase());
        if (compte == null || identifiants.motDePasse() == null
                || !hachage.matches(identifiants.motDePasse(), compte.empreinte())) {
            // Message identique que le compte existe ou non : pas d'énumération des comptes
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("erreur", "Identifiants invalides"));
        }
        Instant maintenant = Instant.now();
        JwtClaimsSet revendications = JwtClaimsSet.builder()
                .issuer(emetteur)
                .subject(identifiants.email().toLowerCase())
                .claim("nom", compte.nom())
                .issuedAt(maintenant)
                .expiresAt(maintenant.plus(DUREE_JETON))
                .build();
        String jeton = encodeur.encode(JwtEncoderParameters.from(
                JwsHeader.with(MacAlgorithm.HS256).build(), revendications)).getTokenValue();
        return ResponseEntity.ok(new Session(jeton, identifiants.email().toLowerCase(), compte.nom(),
                DUREE_JETON.toSeconds()));
    }
}
