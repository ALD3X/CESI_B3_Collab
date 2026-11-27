import { useEffect, useState } from "react";
import { api, euros } from "../api.js";

export default function Catalogue({ session, onCommande, onSessionExpiree }) {
  const [produits, setProduits] = useState(null);
  const [erreur, setErreur] = useState("");
  const [message, setMessage] = useState("");
  const [enCours, setEnCours] = useState(null);

  useEffect(() => {
    api.produits().then(setProduits).catch((e) => setErreur(e.message));
  }, []);

  async function commander(produit) {
    setEnCours(produit.id);
    setMessage("");
    try {
      const commande = await api.commander(session.jeton, produit.id, 1);
      setMessage(`Commande ${commande.id} enregistrée : ${produit.nom} (${euros(commande.montant)}).`);
      onCommande?.();
    } catch (e) {
      if (e.statut === 401) onSessionExpiree?.();
      setMessage(e.message);
    } finally {
      setEnCours(null);
    }
  }

  if (erreur) return <p role="alert" className="alerte">Catalogue indisponible : {erreur}</p>;
  if (!produits) return <p aria-busy="true">Chargement du catalogue…</p>;

  return (
    <>
      <p className="message" role="status" aria-live="polite">{message}</p>
      <ul className="grille-produits">
        {produits.map((p) => (
          <li key={p.id} className="carte-produit">
            <p className="categorie">{p.categorie}</p>
            <h2>{p.nom}</h2>
            <p className="description">{p.description}</p>
            <p className="prix">
              {euros(p.prix_ttc)} <span className="ht">TTC ({euros(p.prix_ht)} HT)</span>
            </p>
            {session ? (
              <button
                type="button"
                className="bouton"
                onClick={() => commander(p)}
                disabled={enCours === p.id}
                aria-label={`Commander ${p.nom}`}
              >
                {enCours === p.id ? "Commande…" : "Commander"}
              </button>
            ) : (
              <p className="indice">Connectez-vous pour commander.</p>
            )}
          </li>
        ))}
      </ul>
    </>
  );
}
