"""Module 4 — Flot maximum (Ford-Fulkerson / Edmonds-Karp) et coupe minimale."""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

from graph import Graph


def _build_residual(g: Graph) -> Dict[str, Dict[str, float]]:
    res: Dict[str, Dict[str, float]] = {v: {} for v in g.vertices}
    for e in g.edges:
        res[e.source][e.target] = res[e.source].get(e.target, 0.0) + e.capacity
        res[e.target].setdefault(e.source, 0.0)
    return res


def _augmenting_path(res, source, sink) -> List[str]:
    """Chaîne améliorante par BFS dans le graphe d'écart."""
    parent = {source: None}
    q = deque([source])
    while q:
        u = q.popleft()
        if u == sink:
            path, cur = [], sink
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return list(reversed(path))
        for v, cap in res[u].items():
            if cap > 0 and v not in parent:
                parent[v] = u
                q.append(v)
    return []


def ford_fulkerson(g: Graph, source: str, sink: str):
    """Flot maximum. Retourne (valeur, flot, graphe d'écart final, chaînes)."""
    if source not in g.adj or sink not in g.adj:
        raise KeyError("Source ou puits inconnu.")
    res = _build_residual(g)
    flow: Dict[Tuple[str, str], float] = {}
    chains: List[List[str]] = []
    value = 0.0

    while True:
        path = _augmenting_path(res, source, sink)
        if not path:
            break
        chains.append(path)
        bottleneck = min(res[u][v] for u, v in zip(path, path[1:]))
        for u, v in zip(path, path[1:]):
            res[u][v] -= bottleneck
            res[v][u] += bottleneck
            flow[(u, v)] = flow.get((u, v), 0.0) + bottleneck
            flow[(v, u)] = flow.get((v, u), 0.0) - bottleneck
        value += bottleneck
    return value, flow, res, chains


def min_cut(g: Graph, source: str, sink: str):
    """Coupe minimale déduite du graphe d'écart final (théorème max-flot/min-coupe)."""
    value, flow, res, _ = ford_fulkerson(g, source, sink)
    # S = sommets atteignables depuis la source dans le graphe d'écart
    S: Set[str] = {source}
    q = deque([source])
    while q:
        u = q.popleft()
        for v, cap in res[u].items():
            if cap > 0 and v not in S:
                S.add(v)
                q.append(v)
    T = set(g.vertices) - S
    cut_edges = [(e.source, e.target, e.capacity)
                 for e in g.edges if e.source in S and e.target in T]
    return value, S, T, cut_edges


def bottlenecks(g: Graph, source: str, sink: str):
    """Identifie les arcs saturés participant à la coupe minimale."""
    _, _, _, cut_edges = min_cut(g, source, sink)
    return cut_edges