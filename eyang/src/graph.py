"""Chargement du reseau et representations en liste et en matrice."""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from collections import namedtuple
from pathlib import Path

import numpy as np

Arc = namedtuple("Arc", "source destination distance temps capacite cout")


class Graphe:
    """Graphe oriente pondere, stocke en liste et en matrice d'adjacence."""

    def __init__(self, stations: list[str], arcs: list[Arc]):
        if len(stations) != len(set(stations)):
            raise ValueError("Liste de stations en double")
        self.stations = list(stations)
        self.index = {nom: i for i, nom in enumerate(self.stations)}
        self.arcs = list(arcs)
        self.adj: dict[str, list[Arc]] = {nom: [] for nom in self.stations}
        self.par_arc: dict[tuple[str, str], Arc] = {}
        for arc in self.arcs:
            if arc.source not in self.index or arc.destination not in self.index:
                raise ValueError(f"Station inconnue dans l'arc {arc.source} -> {arc.destination}")
            cle = (arc.source, arc.destination)
            if cle in self.par_arc:
                raise ValueError(f"Arc en double : {arc.source} -> {arc.destination}")
            self.par_arc[cle] = arc
            self.adj[arc.source].append(arc)
        n = len(self.stations)
        self.present = np.zeros((n, n), dtype=bool)
        self.distance = np.full((n, n), np.inf)
        self.temps = np.full((n, n), np.inf)
        self.capacite = np.zeros((n, n), dtype=float)
        self.cout = np.full((n, n), np.inf)
        for arc in self.arcs:
            i, j = self.index[arc.source], self.index[arc.destination]
            self.present[i, j] = True
            self.distance[i, j] = arc.distance
            self.temps[i, j] = arc.temps
            self.capacite[i, j] = arc.capacite
            self.cout[i, j] = arc.cout

    def nb_sommets(self) -> int:
        return len(self.stations)

    def nb_arcs(self) -> int:
        return len(self.arcs)

    def voisins(self, sommet: str, mode: str = "liste") -> list[str]:
        """Voisins sortants, via la liste ou via la matrice."""
        if sommet not in self.index:
            raise KeyError(sommet)
        if mode == "matrice":
            i = self.index[sommet]
            return [self.stations[j] for j in range(self.nb_sommets()) if self.present[i, j]]
        if mode != "liste":
            raise ValueError(mode)
        return [arc.destination for arc in self.adj[sommet]]

    def a_arc(self, source: str, destination: str, mode: str = "liste") -> bool:
        """Indique si l'arc existe, via la liste ou via la matrice."""
        if source not in self.index or destination not in self.index:
            return False
        if mode == "matrice":
            return bool(self.present[self.index[source], self.index[destination]])
        return any(arc.destination == destination for arc in self.adj[source])

    def arc(self, source: str, destination: str) -> Arc | None:
        return self.par_arc.get((source, destination))

    def poids(self, source: str, destination: str, critere: str = "distance") -> float:
        arc = self.arc(source, destination)
        if arc is None:
            raise KeyError(f"Pas d'arc {source} -> {destination}")
        if critere not in ("distance", "temps", "cout"):
            raise ValueError(f"Critere inconnu : {critere}")
        return getattr(arc, critere)

    def capacite_arc(self, source: str, destination: str) -> float:
        arc = self.arc(source, destination)
        return 0.0 if arc is None else arc.capacite

    def aretes_non_orientees(self) -> list[tuple[str, str, float]]:
        """Aretes non orientees, poids = distance minimale entre les deux sens."""
        meilleur: dict[tuple[str, str], float] = {}
        for arc in self.arcs:
            if arc.source == arc.destination:
                continue
            a, b = sorted((arc.source, arc.destination))
            if (a, b) not in meilleur or arc.distance < meilleur[(a, b)]:
                meilleur[(a, b)] = arc.distance
        return [(a, b, w) for (a, b), w in meilleur.items()]


def _nombre(valeur, ligne: int, nom: str, minimum: float | None = None) -> float:
    try:
        nombre = float(valeur)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Ligne {ligne} : {nom} invalide ({valeur})") from exc
    if not math.isfinite(nombre):
        raise ValueError(f"Ligne {ligne} : {nom} non fini")
    if minimum is not None and nombre < minimum:
        raise ValueError(f"Ligne {ligne} : {nom} doit etre >= {minimum}")
    return nombre


def _arc_depuis(source, destination, distance, temps, capacite, cout, ligne: int) -> Arc:
    source, destination = str(source).strip(), str(destination).strip()
    if not source or not destination:
        raise ValueError(f"Ligne {ligne} : station vide")
    dist = _nombre(distance, ligne, "distance", 0)
    tmp = _nombre(temps, ligne, "temps", 0)
    cap = _nombre(capacite, ligne, "capacite", 0)
    if cout is None or cout == "":
        cout_val = dist
    else:
        cout_val = _nombre(cout, ligne, "cout")
    return Arc(source, destination, dist, tmp, cap, cout_val)


def _stations_des_arcs(arcs: list[Arc], declarees: list[str] | None) -> list[str]:
    if declarees is not None:
        vues = set(declarees)
        for arc in arcs:
            if arc.source not in vues or arc.destination not in vues:
                raise ValueError(f"Station absente de la liste : {arc.source} ou {arc.destination}")
        return declarees
    stations: list[str] = []
    vues: set[str] = set()
    for arc in arcs:
        for nom in (arc.source, arc.destination):
            if nom not in vues:
                vues.add(nom)
                stations.append(nom)
    if not stations:
        raise ValueError("Aucune station dans le fichier")
    return stations


def _lire_texte(chemin: Path) -> Graphe:
    stations: list[str] | None = None
    arcs: list[Arc] = []
    for numero, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        brut = ligne.strip()
        if not brut:
            continue
        if brut.startswith("#"):
            corps = brut[1:].strip()
            bas = corps.lower()
            if bas.startswith("stations"):
                reste = corps.split(":", 1)[1] if ":" in corps else corps.split(None, 1)[1]
                stations = reste.split()
            continue
        if brut.lower().startswith("stations"):
            stations = brut.split()[1:]
            continue
        morceaux = brut.split()
        if len(morceaux) not in (5, 6):
            raise ValueError(
                f"Ligne {numero} : attendu source destination distance temps capacite [cout]"
            )
        cout = morceaux[5] if len(morceaux) == 6 else None
        arcs.append(_arc_depuis(*morceaux[:5], cout, numero))
    return Graphe(_stations_des_arcs(arcs, stations), arcs)


def _lire_csv(chemin: Path) -> Graphe:
    arcs: list[Arc] = []
    with chemin.open(encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.DictReader(fichier)
        if not lecteur.fieldnames:
            raise ValueError("CSV sans en-tete")
        colonnes = {_norm(nom): nom for nom in lecteur.fieldnames}
        for attendu in ("source", "destination", "distance", "temps", "capacite"):
            if attendu not in colonnes:
                raise ValueError(f"Colonne manquante : {attendu}")
        for numero, ligne in enumerate(lecteur, 2):
            if not (ligne.get(colonnes["source"]) or "").strip():
                continue
            cout = ligne.get(colonnes["cout"]) if "cout" in colonnes else None
            arcs.append(
                _arc_depuis(
                    ligne[colonnes["source"]],
                    ligne[colonnes["destination"]],
                    ligne[colonnes["distance"]],
                    ligne[colonnes["temps"]],
                    ligne[colonnes["capacite"]],
                    cout,
                    numero,
                )
            )
    return Graphe(_stations_des_arcs(arcs, None), arcs)


def _lire_json(chemin: Path) -> Graphe:
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    if not isinstance(donnees, dict) or "arcs" not in donnees:
        raise ValueError("JSON attendu : objet avec la cle 'arcs'")
    stations = donnees.get("stations")
    if stations is not None:
        stations = [str(s).strip() for s in stations]
    arcs: list[Arc] = []
    for numero, brut in enumerate(donnees["arcs"], 1):
        if not isinstance(brut, dict):
            raise ValueError(f"Arc {numero} : objet attendu")
        try:
            arcs.append(
                _arc_depuis(
                    brut["source"],
                    brut["destination"],
                    brut["distance"],
                    brut["temps"],
                    brut["capacite"],
                    brut.get("cout"),
                    numero,
                )
            )
        except KeyError as exc:
            raise ValueError(f"Arc {numero} : champ manquant {exc}") from exc
    return Graphe(_stations_des_arcs(arcs, stations), arcs)


def _norm(texte: str) -> str:
    return texte.strip().lower().replace("é", "e").replace("è", "e")


_LECTEURS = {
    "texte": _lire_texte,
    "json": _lire_json,
    "csv": _lire_csv,
}


def detecter_format(chemin: Path) -> str:
    suffixe = chemin.suffix.lower()
    if suffixe == ".json":
        return "json"
    if suffixe == ".csv":
        return "csv"
    if suffixe in {".txt", ".text"}:
        return "texte"
    raise ValueError(f"Extension non reconnue ({suffixe}) : precisez --format")


def charger(chemin: str | Path, format_fichier: str | None = None) -> Graphe:
    """Charge un reseau texte, JSON ou CSV."""
    path = Path(chemin)
    if not path.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    format_effectif = format_fichier or detecter_format(path)
    if format_effectif not in _LECTEURS:
        raise ValueError(f"Format inconnu : {format_effectif}")
    return _LECTEURS[format_effectif](path)


def _taille(obj, vus: set[int] | None = None) -> int:
    if vus is None:
        vus = set()
    ident = id(obj)
    if ident in vus:
        return 0
    vus.add(ident)
    taille = sys.getsizeof(obj)
    if isinstance(obj, dict):
        taille += sum(_taille(cle, vus) + _taille(val, vus) for cle, val in obj.items())
    elif isinstance(obj, (list, tuple, set)):
        taille += sum(_taille(elt, vus) for elt in obj)
    return taille


def comparer_representations(graphe: Graphe, requetes: int = 20000) -> dict:
    """Compare temps d'acces et memoire de la liste et de la matrice."""
    import random

    stations = graphe.stations
    generateur = random.Random(0)
    paires = [
        (generateur.choice(stations), generateur.choice(stations)) for _ in range(requetes)
    ]
    mesures = {}
    for mode, cle_acces, cle_voisins in (
        ("liste", "temps_acces_liste", "temps_voisins_liste"),
        ("matrice", "temps_acces_matrice", "temps_voisins_matrice"),
    ):
        debut = time.perf_counter()
        for source, destination in paires:
            graphe.a_arc(source, destination, mode)
        mesures[cle_acces] = time.perf_counter() - debut
        debut = time.perf_counter()
        for source, _destination in paires:
            graphe.voisins(source, mode)
        mesures[cle_voisins] = time.perf_counter() - debut
    mesures["memoire_liste"] = _taille(graphe.adj)
    mesures["memoire_matrice"] = int(
        graphe.present.nbytes
        + graphe.distance.nbytes
        + graphe.temps.nbytes
        + graphe.capacite.nbytes
        + graphe.cout.nbytes
    )
    mesures["requetes"] = requetes
    mesures["sommets"] = graphe.nb_sommets()
    mesures["arcs"] = graphe.nb_arcs()
    return mesures
