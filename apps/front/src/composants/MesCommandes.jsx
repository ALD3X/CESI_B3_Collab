import { useEffect, useState } from "react";
import { api, euros } from "../api.js";

export default function MesCommandes({ jeton, version, onSessionExpiree }) {
  const [commandes, setCommandes] = useState([]);
  const [erreur, setErreur] = useState("");

  useEffect(() => {
    api.mesCommandes(jeton)
      .then((liste) => {
        setCommandes(liste);
        setErreur("");
      })
      .catch((e) => {
        if (e.statut === 401) onSessionExpiree?.();
        setErreur(e.message);
      });
  }, [jeton, version, onSessionExpiree]);

  return (
    <section aria-labelledby="titre-commandes" className="panneau">
      <h2 id="titre-commandes">Mes commandes</h2>
      {erreur ? <p className="alerte">{erreur}</p> : null}
      {commandes.length === 0 && !erreur ? <p className="indice">Aucune commande pour l'instant.</p> : null}
      <ul className="liste">
        {commandes.slice(0, 8).map((c) => (
          <li key={c.id}>
            <strong>{c.id}</strong> · {euros(c.montant)} · {c.statut === "PAYEE" ? "payée" : c.statut}
          </li>
        ))}
      </ul>
    </section>
  );
}
