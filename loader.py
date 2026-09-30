"""Chargement et validation des données d'entrée (TXT, JSON, CSV)."""
from __future__ import annotations

import csv
import json
import os
from typing import Dict, List

from graph import Edge, Graph


def _edge_from_dict(d: dict) -> Edge:
    src = d.get("source") or d.get("src") or d.get("from")
    dst = d.get("target") or d.get("dst") or d.get("to") or d.get("destination")
    if src is None or dst is None:
        raise ValueError(f"Arc invalide (source/destination manquants) : {d}")
    w = d.get("weight", d.get("poids", d.get("distance", 1.0)))
    return Edge(
        str(src), str(dst),
        distance=float(d.get("distance", w)),
        time=float(d.get("time", d.get("temps", w))),
        capacity=float(d.get("capacity", d.get("capacite", 0.0))),
    )


def load_json(path: str) -> Graph:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    directed = bool(data.get("directed", True))
    g = Graph(directed=directed)
    for v in data.get("vertices", []):
        g.add_vertex(str(v))
    for a in data.get("arcs", data.get("edges", [])):
        g.add_edge(_edge_from_dict(a))
    return g


def load_csv(path: str) -> Graph:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV vide ou sans en-tête.")
        fields = [x.strip().lower() for x in reader.fieldnames]
        directed = True
        g = Graph(directed=directed)
        for row in reader:
            row = {k.strip().lower(): v for k, v in row.items() if k}
            g.add_edge(_edge_from_dict(row))
    return g


def load_text(path: str) -> Graph:
    """Format tabulaire : une ligne par arc, séparateur espace/tabulation.
    Colonnes : source target [distance] [time] [capacity]
    Les lignes commençant par '#' sont ignorées.
    """
    g = Graph(directed=True)
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.replace(",", " ").split()
            if len(parts) < 2:
                raise ValueError(f"Ligne {lineno} invalide : {line!r}")
            src, dst = parts[0], parts[1]
            dist = float(parts[2]) if len(parts) > 2 else 1.0
            tps = float(parts[3]) if len(parts) > 3 else dist
            cap = float(parts[4]) if len(parts) > 4 else 0.0
            g.add_edge(Edge(src, dst, dist, tps, cap))
    return g


def detect_format(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {".json": "json", ".csv": "csv", ".txt": "text"}.get(ext, "text")


def load_graph(path: str, fmt: str | None = None) -> Graph:
    """Charge un graphe depuis un fichier. Détecte le format si non précisé."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    fmt = (fmt or detect_format(path)).lower()
    if fmt in ("json",):
        g = load_json(path)
    elif fmt in ("csv",):
        g = load_csv(path)
    elif fmt in ("text", "txt"):
        g = load_text(path)
    else:
        raise ValueError(f"Format non supporté : {fmt}")
    validate(g)
    return g


def validate(g: Graph) -> None:
    """Vérifie la cohérence basique du réseau."""
    if g.nb_vertices() == 0:
        raise ValueError("Le réseau ne contient aucun sommet.")
    for e in g.edges:
        if e.distance < 0 or e.time < 0:
            raise ValueError(f"Poids négatif interdit en distance/temps : {e}")
        if e.capacity < 0:
            raise ValueError(f"Capacité négative interdite : {e}")