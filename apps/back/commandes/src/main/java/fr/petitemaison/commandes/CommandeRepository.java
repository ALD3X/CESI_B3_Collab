package fr.petitemaison.commandes;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CommandeRepository extends JpaRepository<Commande, String> {

    List<Commande> findByMembreOrderByCreeeLeDesc(String membre);
}
