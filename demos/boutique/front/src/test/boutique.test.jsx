import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import App from "../App.jsx";
import { api, euros } from "../api.js";
import Catalogue from "../composants/Catalogue.jsx";
import Connexion from "../composants/Connexion.jsx";
import MesCommandes from "../composants/MesCommandes.jsx";

const PRODUITS = [
  { id: 1, nom: "Figurine L'Orc", categorie: "figurine", description: "Résine", prix_ht: 49.9, prix_ttc: 59.88, stock: 3 },
  { id: 2, nom: "Fanzine n°38", categorie: "fanzine", description: "Numérique", prix_ht: 4.5, prix_ttc: 4.59, stock: 9 },
];

function reponse(statut, corps) {
  return Promise.resolve(new Response(corps === undefined ? "" : JSON.stringify(corps), { status: statut }));
}

describe("api", () => {
  it("formate les montants en euros", () => {
    expect(euros(59.88)).toMatch(/59,88\s€/);
  });

  it("traduit un 429 en message compréhensible", async () => {
    vi.spyOn(globalThis, "fetch").mockReturnValue(reponse(429));
    await expect(api.commander("jeton", 1)).rejects.toMatchObject({ statut: 429, message: expect.stringMatching(/patientez/) });
  });

  it("tolère une erreur non JSON (proxy)", async () => {
    vi.spyOn(globalThis, "fetch").mockReturnValue(Promise.resolve(new Response("upstream timeout", { status: 504 })));
    await expect(api.produits()).rejects.toMatchObject({ statut: 504 });
  });
});

describe("Catalogue", () => {
  it("affiche les produits avec le prix TTC", async () => {
    vi.spyOn(globalThis, "fetch").mockReturnValue(reponse(200, PRODUITS));
    render(<Catalogue session={null} />);
    expect(await screen.findByRole("heading", { name: "Figurine L'Orc" })).toBeInTheDocument();
    expect(screen.getAllByText(/Connectez-vous pour commander/)).toHaveLength(2);
  });

  it("passe une commande et l'annonce", async () => {
    const fetch = vi.spyOn(globalThis, "fetch")
      .mockReturnValueOnce(reponse(200, PRODUITS))
      .mockReturnValueOnce(reponse(201, { id: "C-1234", montant: 59.88 }));
    const onCommande = vi.fn();
    render(<Catalogue session={{ jeton: "j" }} onCommande={onCommande} />);
    await userEvent.click(await screen.findByRole("button", { name: "Commander Figurine L'Orc" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Commande C-1234 enregistrée");
    expect(onCommande).toHaveBeenCalled();
    expect(fetch.mock.calls[1][1].headers.Authorization).toBe("Bearer j");
  });

  it("signale un catalogue indisponible", async () => {
    vi.spyOn(globalThis, "fetch").mockReturnValue(reponse(503));
    render(<Catalogue session={null} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Catalogue indisponible");
  });
});

describe("Connexion", () => {
  it("affiche une erreur explicite si les identifiants sont faux", async () => {
    vi.spyOn(globalThis, "fetch").mockReturnValue(reponse(401, { erreur: "Identifiants invalides" }));
    render(<Connexion onConnexion={vi.fn()} />);
    await userEvent.type(screen.getByLabelText("Mot de passe"), "faux");
    await userEvent.click(screen.getByRole("button", { name: "Se connecter" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("incorrect");
  });

  it("transmet la session après connexion", async () => {
    const session = { jeton: "j", membre: "morticia@petitemaison.fr", nom: "Morticia" };
    vi.spyOn(globalThis, "fetch").mockReturnValue(reponse(200, session));
    const onConnexion = vi.fn();
    render(<Connexion onConnexion={onConnexion} />);
    await userEvent.type(screen.getByLabelText("Mot de passe"), "Epouvante2026!");
    await userEvent.click(screen.getByRole("button", { name: "Se connecter" }));
    await waitFor(() => expect(onConnexion).toHaveBeenCalledWith(session));
  });
});

describe("MesCommandes", () => {
  it("liste les commandes du membre", async () => {
    vi.spyOn(globalThis, "fetch").mockReturnValue(reponse(200, [{ id: "C-9", montant: 4.59, statut: "PAYEE" }]));
    render(<MesCommandes jeton="j" version={0} />);
    expect(await screen.findByText("C-9")).toBeInTheDocument();
  });
});

describe("App", () => {
  it("affiche la pile technique et le formulaire de connexion", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((url) =>
      url === "/config.json" ? reponse(200, { passerelle: "Kong", bus: "Kafka" }) : reponse(200, PRODUITS));
    render(<App />);
    expect(await screen.findByText("Kong")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Connexion" })).toBeInTheDocument();
  });
});
