package fr.petitemaison.catalogue;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;

/** Règles de prix : TVA française selon la catégorie de produit. */
public final class Tarification {

    /** Presse (fanzine) : taux super-réduit 2,1 %. */
    private static final Map<String, BigDecimal> TAUX_TVA = Map.of("fanzine", new BigDecimal("0.021"));
    /** Autres produits : taux normal 20 %. */
    private static final BigDecimal TAUX_NORMAL = new BigDecimal("0.20");

    private Tarification() {
    }

    public static BigDecimal prixTtc(BigDecimal prixHt, String categorie) {
        if (prixHt.signum() < 0) {
            throw new IllegalArgumentException("Le prix HT ne peut pas être négatif");
        }
        BigDecimal taux = TAUX_TVA.getOrDefault(categorie, TAUX_NORMAL);
        return prixHt.multiply(BigDecimal.ONE.add(taux)).setScale(2, RoundingMode.HALF_UP);
    }
}
