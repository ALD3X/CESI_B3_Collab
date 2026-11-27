import { useState } from "react";
import { api } from "../api.js";

export default function Connexion({ onConnexion }) {
  const [email, setEmail] = useState("morticia@petitemaison.fr");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState("");
  const [enCours, setEnCours] = useState(false);

  async function soumettre(evenement) {
    evenement.preventDefault();
    setErreur("");
    setEnCours(true);
    try {
      onConnexion(await api.connexion(email, motDePasse));
    } catch (e) {
      setErreur(e.statut === 401 ? "Adresse e-mail ou mot de passe incorrect." : e.message);
    } finally {
      setEnCours(false);
    }
  }

  return (
    <section aria-labelledby="titre-connexion" className="panneau">
      <h2 id="titre-connexion">Connexion</h2>
      <form onSubmit={soumettre} noValidate>
        <label htmlFor="email">Adresse e-mail</label>
        <input id="email" type="email" autoComplete="username" required value={email}
               onChange={(e) => setEmail(e.target.value)} />
        <label htmlFor="mot-de-passe">Mot de passe</label>
        <input id="mot-de-passe" type="password" autoComplete="current-password" required value={motDePasse}
               onChange={(e) => setMotDePasse(e.target.value)}
               aria-describedby={erreur ? "erreur-connexion" : undefined} />
        {erreur ? <p id="erreur-connexion" role="alert" className="alerte">{erreur}</p> : null}
        <button type="submit" className="bouton" disabled={enCours}>
          {enCours ? "Connexion…" : "Se connecter"}
        </button>
      </form>
      <p className="indice">Comptes de démo : morticia@, vincent@ ou elvira@petitemaison.fr.</p>
    </section>
  );
}
