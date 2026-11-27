import { useEffect, useState } from "react";

/**
 * Notifications en direct : le service notifications consomme l'événement « commande payée »
 * sur le bus et le pousse au navigateur (Server-Sent Events). La zone est annoncée aux
 * lecteurs d'écran (aria-live) sans voler le focus.
 */
export default function Notifications({ membre }) {
  const [notifications, setNotifications] = useState([]);
  const [connecte, setConnecte] = useState(false);

  useEffect(() => {
    if (typeof EventSource === "undefined") return undefined;
    const source = new EventSource("/api/notifications/flux");
    source.onopen = () => setConnecte(true);
    source.onerror = () => setConnecte(false); // EventSource se reconnecte tout seul
    source.addEventListener("notification", (e) => {
      const n = JSON.parse(e.data);
      if (n.membre === membre) setNotifications((liste) => [n, ...liste].slice(0, 5));
    });
    return () => source.close();
  }, [membre]);

  return (
    <section aria-labelledby="titre-notifications" className="panneau">
      <h2 id="titre-notifications">
        Notifications <span className={connecte ? "pastille ok" : "pastille"}>{connecte ? "en direct" : "hors ligne"}</span>
      </h2>
      <ul className="liste" aria-live="polite">
        {notifications.length === 0 ? <li className="indice">Les confirmations de commande s'afficheront ici.</li> : null}
        {notifications.map((n) => (
          <li key={`${n.commandeId}-${n.recueLe}`} className="notification">{n.message}</li>
        ))}
      </ul>
    </section>
  );
}
