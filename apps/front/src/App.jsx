import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import Catalogue from "./composants/Catalogue.jsx";
import Connexion from "./composants/Connexion.jsx";
import MesCommandes from "./composants/MesCommandes.jsx";
import Notifications from "./composants/Notifications.jsx";

const CLE_SESSION = "pm-session";

function lireSession() {
  try {
    return JSON.parse(sessionStorage.getItem(CLE_SESSION));
  } catch {
    return null;
  }
}

function ecrireSession(session) {
  try {
    if (session) sessionStorage.setItem(CLE_SESSION, JSON.stringify(session));
    else sessionStorage.removeItem(CLE_SESSION);
  } catch {
    // stockage indisponible (navigation privée) : la session reste en mémoire
  }
}

export default function App() {
  const [session, setSession] = useState(lireSession);
  const [config, setConfig] = useState({ passerelle: "…", bus: "…" });
  const [versionCommandes, setVersionCommandes] = useState(0);

  useEffect(() => {
    api.config().then(setConfig);
  }, []);

  const connecter = useCallback((s) => {
    ecrireSession(s);
    setSession(s);
  }, []);

  const deconnecter = useCallback(() => {
    ecrireSession(null);
    setSession(null);
  }, []);

  return (
    <>
      <a className="lien-evitement" href="#contenu">Aller au contenu</a>
      <header className="en-tete">
        <div>
          <p className="marque">La Petite Maison de l'Épouvante</p>
          <p className="sous-titre">Boutique de démonstration</p>
        </div>
        <p className="pile" aria-label="Pile technique utilisée">
          Passerelle : <strong>{config.passerelle}</strong> · Bus : <strong>{config.bus}</strong>
        </p>
        {session ? (
          <div className="compte">
            <span>Bonjour {session.nom}</span>
            <button type="button" className="bouton secondaire" onClick={deconnecter}>
              Se déconnecter
            </button>
          </div>
        ) : null}
      </header>

      <main id="contenu" className="mise-en-page">
        <section aria-labelledby="titre-catalogue" className="colonne-principale">
          <h1 id="titre-catalogue">Catalogue</h1>
          <Catalogue
            session={session}
            onCommande={() => setVersionCommandes((v) => v + 1)}
            onSessionExpiree={deconnecter}
          />
        </section>

        <aside className="colonne-laterale">
          {session ? (
            <>
              <Notifications membre={session.membre} />
              <MesCommandes jeton={session.jeton} version={versionCommandes} onSessionExpiree={deconnecter} />
            </>
          ) : (
            <Connexion onConnexion={connecter} />
          )}
        </aside>
      </main>
    </>
  );
}
