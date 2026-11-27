// Accès à l'API, toujours à travers la passerelle (chemins relatifs /api/...).

export class ErreurApi extends Error {
  constructor(statut, message) {
    super(message);
    this.statut = statut;
  }
}

const MESSAGES = {
  401: "Session expirée ou identifiants invalides.",
  429: "Trop de demandes en même temps : patientez une seconde puis réessayez.",
  502: "Service momentanément indisponible, réessayez dans quelques instants.",
  503: "Service momentanément indisponible, réessayez dans quelques instants.",
  504: "Service momentanément indisponible, réessayez dans quelques instants.",
};

async function appel(chemin, { methode = "GET", jeton, corps } = {}) {
  const entetes = { Accept: "application/json" };
  if (corps !== undefined) entetes["Content-Type"] = "application/json";
  if (jeton) entetes.Authorization = `Bearer ${jeton}`;
  const reponse = await fetch(chemin, {
    method: methode,
    headers: entetes,
    body: corps === undefined ? undefined : JSON.stringify(corps),
  });
  const texte = await reponse.text();
  let donnees = null;
  try {
    donnees = texte ? JSON.parse(texte) : null;
  } catch {
    donnees = null; // réponse non JSON (ex. erreur brute d'un proxy)
  }
  if (!reponse.ok) {
    throw new ErreurApi(reponse.status, MESSAGES[reponse.status] ?? donnees?.erreur ?? `Erreur ${reponse.status}`);
  }
  return donnees;
}

export const api = {
  config: () => appel("/config.json").catch(() => ({ passerelle: "?", bus: "?" })),
  connexion: (email, motDePasse) =>
    appel("/api/identite/connexion", { methode: "POST", corps: { email, motDePasse } }),
  produits: () => appel("/api/catalogue/produits"),
  commander: (jeton, produitId, quantite = 1) =>
    appel("/api/commandes", { methode: "POST", jeton, corps: { lignes: [{ produitId, quantite }] } }),
  mesCommandes: (jeton) => appel("/api/commandes", { jeton }),
};

export const euros = (montant) =>
  new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(montant);
