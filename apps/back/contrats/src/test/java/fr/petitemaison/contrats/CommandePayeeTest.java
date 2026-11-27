package fr.petitemaison.contrats;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

class CommandePayeeTest {

    private static CommandePayee commande(String montant, int version) {
        return new CommandePayee(version, "C-1", "membre@petitemaison.fr", new BigDecimal(montant),
                List.of(new CommandePayee.Ligne(1, "Figurine", 1)), Instant.now());
    }

    @Test
    void commandeValide() {
        assertTrue(commande("59.88", CommandePayee.VERSION).estValide());
    }

    @Test
    void montantNegatifInvalide() {
        assertFalse(commande("-5", CommandePayee.VERSION).estValide());
    }

    @Test
    void versionInconnueInvalide() {
        assertFalse(commande("10", 99).estValide());
    }
}
