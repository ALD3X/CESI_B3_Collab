"""Mesures sur la boutique démarrée (python tools/boutique.py demarrer).

  - Passerelles : latence ajoutée (direct :8085 contre Spring :8080 et Kong :8000), mémoire, taille d'image,
    démarrage, lignes de code/configuration à maintenir ;
  - Bus d'événements courant : délai entre la commande et la notification reçue en direct (SSE),
    mémoire et taille d'image du broker.

Usage :  python tools/scenarios/mesures.py [--requetes 1000] [--commandes 40]
Résultats : tools/resultats/mesures-<bus>.json
"""

from __future__ import annotations

import argparse
import http.client as client_http
import json
import re
import statistics
import threading
import time

from outils import RACINE, commander, connexion, docker, etat

PASSERELLES = {
    "spring": {"port": 8080, "conteneurs": ["boutique-passerelle-spring-1", "boutique-redis-1"],
               "images": ["boutique-passerelle", "redis:7.4-alpine"],
               "fichiers": ["apps/back/passerelle/src/main/resources/application.yml",
                            "apps/back/passerelle/src/main/java/**/*.java", "apps/back/passerelle/pom.xml"]},
    "kong": {"port": 8000, "conteneurs": ["boutique-kong-1"], "images": ["boutique-kong"], "fichiers": ["infra/kong/kong.yml"]},
}
BROKERS = {"rabbit": (["boutique-rabbitmq-1"], ["rabbitmq:3.13-management"]),
           "kafka": (["boutique-kafka-1"], ["apache/kafka:3.8.1"])}


def memoire_mio(conteneur: str) -> float:
    brut = docker("stats", "--no-stream", "--format", "{{.MemUsage}}", conteneur).split("/")[0].strip()
    valeur, unite = re.match(r"([\d.]+)\s*([KMG]i?B)", brut).groups()
    return float(valeur) * {"KiB": 1 / 1024, "MiB": 1, "GiB": 1024, "KB": 1 / 1024, "MB": 1, "GB": 1024}[unite]


def taille_images(images: list[str]) -> int:
    return round(sum(int(docker("image", "inspect", "--format", "{{.Size}}", i)) for i in images) / 1024**2)


def latences(port: int, n: int) -> list[float]:
    conn = client_http.HTTPConnection("localhost", port, timeout=10)
    mesures = []
    for i in range(n + 200):
        t = time.perf_counter()
        conn.request("GET", "/api/catalogue/produits/1")
        rep = conn.getresponse()
        rep.read()
        if rep.status != 200:
            raise RuntimeError(f"port {port} : réponse {rep.status}")
        if i >= 200:   # échauffement non mesuré
            mesures.append((time.perf_counter() - t) * 1000)
    conn.close()
    return mesures


def demarrage(conteneur: str, port: int) -> float:
    docker("restart", "-t", "5", conteneur)
    debut = time.perf_counter()
    while time.perf_counter() - debut < 120:
        try:
            conn = client_http.HTTPConnection("localhost", port, timeout=1)
            conn.request("GET", "/api/catalogue/produits/1")
            if conn.getresponse().status == 200:
                return time.perf_counter() - debut
        except OSError:
            pass
        time.sleep(0.05)
    raise TimeoutError(conteneur)


def lignes_utiles(motifs: list[str]) -> int:
    total = 0
    for motif in motifs:
        for fichier in RACINE.glob(motif):
            for ligne in fichier.read_text(encoding="utf-8").splitlines():
                texte = ligne.strip()
                if texte and not texte.startswith(("#", "//", "*", "/*", "<!--")):
                    total += 1
    return total


def delai_notifications(nb: int) -> list[float]:
    """Délai entre l'envoi d'une commande et la réception de sa notification sur le flux SSE.
    La notification arrive souvent AVANT la réponse HTTP de la commande : on associe après coup."""
    envois: dict[str, float] = {}
    recus: dict[str, float] = {}
    pret = threading.Event()

    def ecouter() -> None:
        conn = client_http.HTTPConnection("localhost", 8080, timeout=60)
        conn.request("GET", "/api/notifications/flux")
        rep = conn.getresponse()
        pret.set()
        while len(recus) < nb:
            ligne = rep.readline().decode()   # flux décodé (réponse HTTP découpée en blocs)
            if ligne.startswith("data:{"):
                recus[json.loads(ligne[5:])["commandeId"]] = time.perf_counter()

    fil = threading.Thread(target=ecouter, daemon=True)
    fil.start()
    pret.wait(10)
    time.sleep(0.5)
    jetons = [connexion(m, 8080) for m in ("morticia", "vincent", "elvira")]
    for i in range(nb):
        conn = client_http.HTTPConnection("localhost", 8080, timeout=10)
        t = time.perf_counter()
        conn.request("POST", "/api/commandes", body=json.dumps({"lignes": [{"produitId": 2, "quantite": 1}]}),
                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {jetons[i % 3]}"})
        rep = conn.getresponse()
        corps = json.loads(rep.read())
        envois[corps["id"]] = t
        time.sleep(0.15)
    fil.join(30)
    return [(recus[c] - envois[c]) * 1000 for c in envois if c in recus]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--requetes", type=int, default=1000)
    parser.add_argument("--commandes", type=int, default=40)
    args = parser.parse_args()
    bus = etat()["bus"]
    resultats: dict = {"bus": bus}

    print("▶ Passerelles")
    direct = latences(8085, args.requetes)
    ref50, ref95 = statistics.median(direct), statistics.quantiles(direct, n=20)[18]
    for nom, p in PASSERELLES.items():
        lat = latences(p["port"], args.requetes)
        resultats[nom] = {
            "latence_ajoutee_p50_ms": round(statistics.median(lat) - ref50, 2),
            "latence_ajoutee_p95_ms": round(statistics.quantiles(lat, n=20)[18] - ref95, 2),
            "memoire_mio": round(sum(memoire_mio(c) for c in p["conteneurs"])),
            "image_mio": taille_images(p["images"]),
            "demarrage_s": round(statistics.median(demarrage(p["conteneurs"][0], p["port"]) for _ in range(3)), 2),
            "lignes_a_maintenir": lignes_utiles(p["fichiers"]),
            "conteneurs": len(p["conteneurs"]),
        }
    print(f"{'Mesure':<30}{'Spring Cloud GW':>17}{'Kong 3.9':>12}")
    for cle in resultats["spring"]:
        print(f"{cle:<30}{resultats['spring'][cle]:>17}{resultats['kong'][cle]:>12}")

    print(f"\n▶ Bus d'événements : {bus}")
    delais = delai_notifications(args.commandes)
    conteneurs, images = BROKERS[bus]
    resultats["bus_mesures"] = {
        "commande_vers_notification_p50_ms": round(statistics.median(delais), 1),
        "commande_vers_notification_p95_ms": round(statistics.quantiles(delais, n=20)[18], 1),
        "notifications_recues": f"{len(delais)}/{args.commandes}",
        "memoire_broker_mio": round(sum(memoire_mio(c) for c in conteneurs)),
        "image_broker_mio": taille_images(images),
    }
    for cle, valeur in resultats["bus_mesures"].items():
        print(f"{cle:<36}{valeur:>12}")

    sortie = RACINE / "tools" / "resultats" / f"mesures-{bus}.json"
    sortie.parent.mkdir(exist_ok=True)
    sortie.write_text(json.dumps(resultats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nRésultats enregistrés : {sortie.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
