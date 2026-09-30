"""Module 1 — Exploration du réseau : DFS, BFS, composantes, CCS."""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Set

from graph import Graph


# ----------------------------- Parcours -----------------------------
def dfs(g: Graph, source: str) -> List[str]:
    """Parcours en profondeur itératif depuis `source`."""
    if source not in g.adj:
        raise KeyError(f"Sommet inconnu : {source}")
    visited: Set[str] = set()
    order: List[str] = []
    stack = [source]
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        for e in reversed(g.neighbors(u)):
            if e.target not in visited:
                stack.append(e.target)
    return order


def bfs(g: Graph, source: str) -> List[str]:
    """Parcours en largeur depuis `source`."""
    if source not in g.adj:
        raise KeyError(f"Sommet inconnu : {source}")
    visited = {source}
    order = [source]
    q = deque([source])
    while q:
        u = q.popleft()
        for e in g.neighbors(u):
            if e.target not in visited:
                visited.add(e.target)
                order.append(e.target)
                q.append(e.target)
    return order


def reachable_from(g: Graph, source: str) -> Set[str]:
    """Toutes les stations accessibles depuis `source`."""
    return set(bfs(g, source))


def distances_bfs(g: Graph, source: str) -> Dict[str, int]:
    """Nombre d'arcs minimal depuis `source` (graphe non pondéré)."""
    dist = {source: 0}
    q = deque([source])
    while q:
        u = q.popleft()
        for e in g.neighbors(u):
            if e.target not in dist:
                dist[e.target] = dist[u] + 1
                q.append(e.target)
    return dist


# ------------------------ Composantes connexes ----------------------
def weak_components(g: Graph) -> List[List[str]]:
    """Composantes connexes (direction ignorée)."""
    adj: Dict[str, Set[str]] = {v: set() for v in g.vertices}
    for e in g.edges:
        adj[e.source].add(e.target)
        adj[e.target].add(e.source)
    seen: Set[str] = set()
    comps: List[List[str]] = []
    for v in g.vertices:
        if v in seen:
            continue
        comp, stack = [], [v]
        seen.add(v)
        while stack:
            u = stack.pop()
            comp.append(u)
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        comps.append(sorted(comp))
    return comps


def is_weakly_connected(g: Graph) -> bool:
    return len(weak_components(g)) <= 1


def strongly_connected_components(g: Graph) -> List[List[str]]:
    """Algorithme de Kosaraju (2 DFS)."""
    # 1er passage : ordre de fin de visite
    visited: Set[str] = set()
    order: List[str] = []

    def _dfs1(start: str) -> None:
        stack = [(start, iter(g.neighbors(start)))]
        visited.add(start)
        while stack:
            node, it = stack[-1]
            advanced = False
            for e in it:
                if e.target not in visited:
                    visited.add(e.target)
                    stack.append((e.target, iter(g.neighbors(e.target))))
                    advanced = True
                    break
            if not advanced:
                order.append(node)
                stack.pop()

    for v in g.vertices:
        if v not in visited:
            _dfs1(v)

    # 2e passage sur le graphe inversé
    gr = g.reversed()
    visited.clear()
    comps: List[List[str]] = []
    for v in reversed(order):
        if v in visited:
            continue
        comp, stack = [], [v]
        visited.add(v)
        while stack:
            u = stack.pop()
            comp.append(u)
            for e in gr.neighbors(u):
                if e.target not in visited:
                    visited.add(e.target)
                    stack.append(e.target)
        comps.append(sorted(comp))
    return comps


def is_strongly_connected(g: Graph) -> bool:
    return len(strongly_connected_components(g)) <= 1