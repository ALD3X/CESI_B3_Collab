package fr.petitemaison.commandes;

import fr.petitemaison.contrats.CommandePayee;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.stream.function.StreamBridge;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/commandes")
public class CommandesController {

    static final String SORTIE = "commandesPayees-out-0";

    public record LigneDemandee(long produitId, int quantite) {
    }

    public record NouvelleCommande(List<LigneDemandee> lignes) {
    }

    private final CommandeRepository commandes;
    private final CatalogueClient catalogue;
    private final StreamBridge bus;
    private final boolean demoActive;

    public CommandesController(CommandeRepository commandes, CatalogueClient catalogue, StreamBridge bus,
                               @Value("${boutique.demo.evenement-invalide:false}") boolean demoActive) {
        this.commandes = commandes;
        this.catalogue = catalogue;
        this.bus = bus;
        this.demoActive = demoActive;
    }

    @GetMapping
    public List<Commande> mesCommandes(@AuthenticationPrincipal Jwt jeton) {
        return commandes.findByMembreOrderByCreeeLeDesc(jeton.getSubject());
    }

    @PostMapping
    public ResponseEntity<?> commander(@AuthenticationPrincipal Jwt jeton, @RequestBody NouvelleCommande demande) {
        if (demande.lignes() == null || demande.lignes().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("erreur", "La commande est vide"));
        }
        List<Commande.Ligne> lignes = new ArrayList<>();
        for (LigneDemandee ligne : demande.lignes()) {
            if (ligne.quantite() < 1 || ligne.quantite() > 10) {
                return ResponseEntity.badRequest().body(Map.of("erreur", "Quantité entre 1 et 10"));
            }
            var produit = catalogue.produit(ligne.produitId());
            if (produit.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("erreur", "Produit inconnu : " + ligne.produitId()));
            }
            lignes.add(new Commande.Ligne(produit.get().id(), produit.get().nom(), ligne.quantite(),
                    produit.get().prixTtc()));
        }
        Commande commande = commandes.save(new Commande(jeton.getSubject(), lignes));
        // Publication après l'enregistrement. En production : patron « outbox » pour garantir les deux ensemble.
        bus.send(SORTIE, new CommandePayee(CommandePayee.VERSION, commande.getId(), commande.getMembre(),
                commande.getMontant(),
                lignes.stream().map(l -> new CommandePayee.Ligne(l.produitId(), l.nom(), l.quantite())).toList(),
                commande.getCreeeLe()));
        return ResponseEntity.status(HttpStatus.CREATED).body(commande);
    }

    /** Démo « événement poison » : publie un événement invalide (montant négatif). Désactivé hors démo. */
    @PostMapping("/demo/evenement-invalide")
    public ResponseEntity<?> evenementInvalide(@AuthenticationPrincipal Jwt jeton) {
        if (!demoActive) {
            return ResponseEntity.notFound().build();
        }
        bus.send(SORTIE, new CommandePayee(CommandePayee.VERSION, "C-POISON", jeton.getSubject(),
                new BigDecimal("-5.00"), List.of(), Instant.now()));
        return ResponseEntity.accepted().body(Map.of("publie", "C-POISON"));
    }
}
