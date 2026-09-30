"""Module 3 — Plus courts chemins et fermeture transitive."""
from __future__ import annotations

import heapq
from typing import Dict, List, Set, Tuple

from graph import Graph

INF = float("inf")


# ------------------------------ Dijkstra ------------------------------
def dijkstra(g: Graph, source: str, criterion: str = "distance"):
    """Retourne (distances, prédécesseurs). Poids >= 0 exigés."""
    if source not in g.adj:
        raise KeyError(f"Sommet inconnu : {source}")
    dist = {v: INF for v in g.vertices}
    prev = {v: None for v in g.vertices}
    dist[source] = 0.0
    pq = [(0.0, source)]
    done: Set[str] = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        for e in g.neighbors(u):
            w = e.weight(criterion)
            if w < 0:
                raise ValueError("Dijkstra exige des poids positifs ou nuls.")
            nd = d + w
            if nd < dist[e.target]:
                dist[e.target] = nd
                prev[e.target] = u
                heapq.heappush(pq, (nd, e.target))
    return dist, prev


# ---------------------------- Bellman-Ford ----------------------------
def bellman_ford(g: Graph, source: str, criterion: str = "distance"):
    """Gère les poids négatifs. Détecte les cycles de poids négatif."""
    if source not in g.adj:
        raise KeyError(f"Sommet inconnu : {source}")
    dist = {v: INF for v in g.vertices}
    prev = {v: None for v in g.vertices}
    dist[source] = 0.0
    n = g.nb_vertices()
    for _ in range(n - 1):
        updated = False
        for e in g.edges:
            if dist[e.source] == INF:
                continue
            nd = dist[e.source] + e.weight(criterion)
            if nd < dist[e.target]:
                dist[e.target] = nd
                prev[e.target] = e.source
                updated = True
        if not updated:
            break
    # détection de cycle négatif
    for e in g.edges:
        if dist[e.source] != INF and dist[e.source] + e.weight(criterion) < dist[e.target]:
            raise ValueError("Cycle de poids négatif détecté.")
    return dist, prev


# --------------------------- Reconstruction ---------------------------
def build_path(prev: Dict[str, str | None], source: str, target: str) -> List[str]:
    if source == target:
        return [source]
    path, cur = [], target
    while cur is not None and cur != source:
        path.append(cur)
        cur = prev.get(cur)
    if cur != source:
        return []
    path.append(source)
    return list(reversed(path))


def shortest_path(g: Graph, source: str, target: str,
                  criterion: str = "distance", algorithm: str = "dijkstra"):
    algo = algorithm.lower()
    if algo in ("dijkstra", "moore-dijkstra"):
        dist, prev = dijkstra(g, source, criterion)
    elif algo in ("bellman", "bellman-ford"):
        dist, prev = bellman_ford(g, source, criterion)
    else:
        raise ValueError(f"Algorithme inconnu : {algorithm}")
    return dist.get(target, INF), build_path(prev, source, target)


# ------------------------ Fermeture transitive ------------------------
def transitive_closure(g: Graph) -> Dict[str, Set[str]]:
    """Pour chaque sommet, l'ensemble des sommets atteignables."""
    closure: Dict[str, Set[str]] = {}
    for v in g.vertices:
        seen, stack = set(), [v]
        while stack:
            u = stack.pop()
            for e in g.neighbors(u):
                if e.target not in seen:
                    seen.add(e.target)
                    stack.append(e.target)
        closure[v] = seen
    return closure


def closure_matrix(g: Graph):
    """Matrice booléenne de la fermeture transitive (Floyd-Warshall booléen)."""
    import numpy as np
    idx = g.index()
    n = len(idx)
    R = np.zeros((n, n), dtype=bool)
    np.fill_diagonal(R, True)
    for e in g.edges:
        R[idx[e.source], idx[e.target]] = True
    for k in range(n):
        R |= R[:, k][:, None] & R[k, :][None, :]
    return R, idx


def centrality(g: Graph, criterion: str = "distance") -> List[Tuple[str, float]]:
    """Centralité de proximité (somme des distances aux autres stations)."""
    result = []
    for v in g.vertices:
        dist, _ = dijkstra(g, v, criterion)
        total = sum(d for u, d in dist.items() if u != v and d < INF)
        result.append((v, total))
    result.sort(key=lambda t: t[1])
    return result