"""Arbres couvrants minimum : Kruskal et Prim, poids = distance."""

from __future__ import annotations

import heapq
from collections import defaultdict
from dataclasses import dataclass

from .graph import Graphe


@dataclass(frozen=True)
class Arbre:
    aretes: list[tuple[str, str, float]]
    cout: float

    @property
    def nb_aretes(self) -> int:
        return len(self.aretes)


def _connexe(graphe: Graphe, nb_aretes: int) -> bool:
    n = graphe.nb_sommets()
    return n <= 1 or nb_aretes == n - 1


def kruskal(graphe: Graphe) -> tuple[Arbre, bool]:
    """Foret couvrante minimum par Kruskal."""
    parent = {station: station for station in graphe.stations}
    rang = {station: 0 for station in graphe.stations}

    def trouver(sommet: str) -> str:
        while parent[sommet] != sommet:
            parent[sommet] = parent[parent[sommet]]
            sommet = parent[sommet]
        return sommet

    def unir(a: str, b: str) -> bool:
        ra, rb = trouver(a), trouver(b)
        if ra == rb:
            return False
        if rang[ra] < rang[rb]:
            parent[ra] = rb
        elif rang[ra] > rang[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rang[ra] += 1
        return True

    choisis = []
    for a, b, poids in sorted(graphe.aretes_non_orientees(), key=lambda e: (e[2], e[0], e[1])):
        if unir(a, b):
            choisis.append((a, b, poids))
    return Arbre(choisis, sum(p for _, _, p in choisis)), _connexe(graphe, len(choisis))


def prim(graphe: Graphe) -> tuple[Arbre, bool]:
    """Foret couvrante minimum par Prim."""
    adj: dict[str, list[tuple[float, str]]] = defaultdict(list)
    for a, b, poids in graphe.aretes_non_orientees():
        adj[a].append((poids, b))
        adj[b].append((poids, a))
    restants = set(graphe.stations)
    choisis = []
    while restants:
        depart = next(station for station in graphe.stations if station in restants)
        restants.remove(depart)
        tas = [(poids, depart, voisin) for poids, voisin in adj[depart]]
        heapq.heapify(tas)
        while tas:
            poids, origine, voisin = heapq.heappop(tas)
            if voisin not in restants:
                continue
            restants.remove(voisin)
            a, b = (origine, voisin) if origine < voisin else (voisin, origine)
            choisis.append((a, b, poids))
            for poids_suivant, autre in adj[voisin]:
                if autre in restants:
                    heapq.heappush(tas, (poids_suivant, voisin, autre))
    choisis.sort(key=lambda e: (e[2], e[0], e[1]))
    return Arbre(choisis, sum(p for _, _, p in choisis)), _connexe(graphe, len(choisis))
