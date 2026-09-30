"""Module 2 — Arbre couvrant minimum (Kruskal et Prim)."""
from __future__ import annotations

import heapq
from typing import Dict, List, Tuple

from graph import Graph

MSTResult = Tuple[List[Tuple[str, str, float]], float]


class UnionFind:
    def __init__(self, elems):
        self.parent = {x: x for x in elems}
        self.rank = {x: 0 for x in elems}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def _undirected_edge_list(g: Graph, criterion: str):
    """Liste (u, v, poids) non orientée, en gardant le poids minimal."""
    best: Dict[Tuple[str, str], float] = {}
    for e in g.edges:
        u, v = sorted((e.source, e.target))
        w = e.weight(criterion)
        if (u, v) not in best or w < best[(u, v)]:
            best[(u, v)] = w
    return [(u, v, w) for (u, v), w in best.items()]


def kruskal(g: Graph, criterion: str = "distance") -> MSTResult:
    """Arbre couvrant minimum par l'algorithme de Kruskal."""
    edges = sorted(_undirected_edge_list(g, criterion), key=lambda t: t[2])
    uf = UnionFind(g.vertices)
    mst, total = [], 0.0
    for u, v, w in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            total += w
    return mst, total


def prim(g: Graph, criterion: str = "distance", start: str | None = None) -> MSTResult:
    """Arbre couvrant minimum par l'algorithme de Prim (tas binaire)."""
    verts = g.vertices
    if not verts:
        return [], 0.0
    start = start or verts[0]

    # adjacence non orientée avec poids minimal
    adj: Dict[str, Dict[str, float]] = {v: {} for v in verts}
    for u, v, w in _undirected_edge_list(g, criterion):
        if v not in adj[u] or w < adj[u][v]:
            adj[u][v] = w
        if u not in adj[v] or w < adj[v][u]:
            adj[v][u] = w

    visited = {start}
    heap = [(w, start, v) for v, w in adj[start].items()]
    heapq.heapify(heap)
    mst, total = [], 0.0
    while heap and len(visited) < len(verts):
        w, u, v = heapq.heappop(heap)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, w))
        total += w
        for x, wx in adj[v].items():
            if x not in visited:
                heapq.heappush(heap, (wx, v, x))
    return mst, total