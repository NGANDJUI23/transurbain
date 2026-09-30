"""Module 1 — Représentation en mémoire du réseau de transport.

Deux représentations sont fournies :
  * liste d'adjacence  -> classe Graph
  * matrice d'adjacence -> Graph.adjacency_matrix()

Chaque arc porte : distance (km), temps (min), capacité (passagers/h).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

CRITERIA = ("distance", "time", "capacity")


@dataclass
class Edge:
    """Arc orienté du réseau."""
    source: str
    target: str
    distance: float = 1.0
    time: float = 1.0
    capacity: float = 0.0

    def weight(self, criterion: str = "distance") -> float:
        if criterion not in CRITERIA:
            raise ValueError(f"Critère inconnu : {criterion} (attendu : {CRITERIA})")
        return float(getattr(self, criterion))

    def __repr__(self) -> str:  # pragma: no cover
        return (f"Edge({self.source}->{self.target}, d={self.distance}, "
                f"t={self.time}, c={self.capacity})")


class Graph:
    """Graphe orienté pondéré (ou non orienté si directed=False)."""

    def __init__(self, directed: bool = True) -> None:
        self.directed = directed
        self._adj: Dict[str, List[Edge]] = {}
        self._edges: List[Edge] = []
        self._vertices: List[str] = []

    # ---------- Construction ----------
    def add_vertex(self, v: str) -> None:
        if v not in self._adj:
            self._adj[v] = []
            self._vertices.append(v)

    def add_edge(self, e: Edge) -> None:
        self.add_vertex(e.source)
        self.add_vertex(e.target)
        self._edges.append(e)
        self._adj[e.source].append(e)
        if not self.directed:
            self._adj[e.target].append(
                Edge(e.target, e.source, e.distance, e.time, e.capacity)
            )

    # ---------- Accès ----------
    @property
    def vertices(self) -> List[str]:
        return list(self._vertices)

    @property
    def edges(self) -> List[Edge]:
        return list(self._edges)

    @property
    def adj(self) -> Dict[str, List[Edge]]:
        return self._adj

    def neighbors(self, v: str) -> List[Edge]:
        return self._adj.get(v, [])

    def nb_vertices(self) -> int:
        return len(self._vertices)

    def nb_edges(self) -> int:
        return len(self._edges)

    def index(self) -> Dict[str, int]:
        return {v: i for i, v in enumerate(self._vertices)}

    # ---------- Représentation matricielle ----------
    def adjacency_matrix(self, criterion: str = "distance",
                         default: float = np.inf) -> Tuple[np.ndarray, Dict[str, int]]:
        """Retourne (matrice, index). M[i,j] = poids de l'arc i->j (default si absent)."""
        idx = self.index()
        n = len(idx)
        M = np.full((n, n), default, dtype=float)
        np.fill_diagonal(M, 0.0)
        for e in self._edges:
            i, j = idx[e.source], idx[e.target]
            w = e.weight(criterion)
            if M[i, j] == default or w < M[i, j]:
                M[i, j] = w
        return M, idx

    def capacity_matrix(self) -> Tuple[np.ndarray, Dict[str, int]]:
        idx = self.index()
        n = len(idx)
        C = np.zeros((n, n), dtype=float)
        for e in self._edges:
            C[idx[e.source], idx[e.target]] += e.capacity
        return C, idx

    # ---------- Graphe inversé (pour Kosaraju) ----------
    def reversed(self) -> "Graph":
        g = Graph(directed=True)
        for v in self._vertices:
            g.add_vertex(v)
        for e in self._edges:
            g.add_edge(Edge(e.target, e.source, e.distance, e.time, e.capacity))
        return g

    def undirected_copy(self) -> "Graph":
        g = Graph(directed=False)
        seen = set()
        for e in self._edges:
            key = tuple(sorted((e.source, e.target)))
            if key in seen:
                continue
            seen.add(key)
            g.add_edge(Edge(e.source, e.target, e.distance, e.time, e.capacity))
        return g

    def __repr__(self) -> str:  # pragma: no cover
        kind = "orienté" if self.directed else "non orienté"
        return f"Graph({kind}, {self.nb_vertices()} sommets, {self.nb_edges()} arcs)"


# ------------------------------------------------------------------
# Comparaison des deux représentations (temps d'accès / mémoire)
# ------------------------------------------------------------------
def compare_representations(g: Graph, criterion: str = "distance",
                            repeats: int = 2000) -> Dict[str, float]:
    """Compare listes vs matrices : temps d'accès et occupation mémoire."""
    import sys
    import time

    M, idx = g.adjacency_matrix(criterion, default=np.inf)
    n = g.nb_vertices()
    verts = g.vertices

    # --- temps d'accès (voisinage complet d'un sommet) ---
    t0 = time.perf_counter()
    for _ in range(repeats):
        for v in verts:
            for e in g.neighbors(v):
                _ = e.weight(criterion)
    t_list = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(repeats):
        for v in verts:
            i = idx[v]
            for j in range(n):
                if M[i, j] not in (np.inf, 0.0):
                    _ = M[i, j]
    t_matrix = time.perf_counter() - t0

    # --- occupation mémoire (ordre de grandeur) ---
    mem_list = sys.getsizeof(g._adj) + sum(
        sys.getsizeof(lst) + sum(sys.getsizeof(e) for e in lst)
        for lst in g._adj.values()
    )
    mem_matrix = M.nbytes

    return {
        "temps_liste_s": t_list,
        "temps_matrice_s": t_matrix,
        "memoire_liste_octets": mem_list,
        "memoire_matrice_octets": mem_matrix,
        "densite": g.nb_edges() / (n * (n - 1)) if n > 1 else 0.0,
    }