"""Parcours DFS et BFS, connexite et composantes fortement connexes."""

from __future__ import annotations

from collections import deque

from .graph import Graphe


def parcours_dfs(graphe: Graphe, source: str) -> dict:
    """Parcours en profondeur depuis source. Retourne ordre et parents."""
    if source not in graphe.index:
        raise KeyError(source)
    vus = {source}
    pile = [source]
    ordre = []
    parents = {source: None}
    while pile:
        sommet = pile.pop()
        ordre.append(sommet)
        for voisin in reversed(graphe.voisins(sommet)):
            if voisin not in vus:
                vus.add(voisin)
                parents[voisin] = sommet
                pile.append(voisin)
    return {"ordre": ordre, "parents": parents}


def parcours_bfs(graphe: Graphe, source: str) -> dict:
    """Parcours en largeur depuis source. Retourne ordre et parents."""
    if source not in graphe.index:
        raise KeyError(source)
    vus = {source}
    file = deque([source])
    ordre = []
    parents = {source: None}
    while file:
        sommet = file.popleft()
        ordre.append(sommet)
        for voisin in graphe.voisins(sommet):
            if voisin not in vus:
                vus.add(voisin)
                parents[voisin] = sommet
                file.append(voisin)
    return {"ordre": ordre, "parents": parents}


def accessibles(graphe: Graphe, source: str) -> list[str]:
    """Stations atteignables depuis source, sens des arcs conserve."""
    return parcours_bfs(graphe, source)["ordre"]


def _adjacence_non_orientee(graphe: Graphe) -> dict[str, list[str]]:
    adj = {nom: [] for nom in graphe.stations}
    for a, b, _poids in graphe.aretes_non_orientees():
        adj[a].append(b)
        adj[b].append(a)
    return adj


def composantes_connexes(graphe: Graphe) -> list[list[str]]:
    """Composantes connexes du reseau ignore l'orientation."""
    adj = _adjacence_non_orientee(graphe)
    vus: set[str] = set()
    composantes = []
    for depart in graphe.stations:
        if depart in vus:
            continue
        pile = [depart]
        vus.add(depart)
        comp = []
        while pile:
            sommet = pile.pop()
            comp.append(sommet)
            for voisin in adj[sommet]:
                if voisin not in vus:
                    vus.add(voisin)
                    pile.append(voisin)
        composantes.append(sorted(comp))
    return composantes


def est_connexe(graphe: Graphe) -> bool:
    """Vrai si toutes les stations sont reliees en ignorant l'orientation."""
    return len(composantes_connexes(graphe)) <= 1


def composantes_fortement_connexes(graphe: Graphe) -> list[list[str]]:
    """Composantes fortement connexes (Kosaraju)."""
    adj = {nom: graphe.voisins(nom) for nom in graphe.stations}
    transpose: dict[str, list[str]] = {nom: [] for nom in graphe.stations}
    for source, voisins in adj.items():
        for destination in voisins:
            transpose[destination].append(source)

    vus: set[str] = set()
    fin: list[str] = []

    def visiter(depart: str) -> None:
        pile = [(depart, 0)]
        vus.add(depart)
        while pile:
            sommet, indice = pile[-1]
            voisins = adj[sommet]
            if indice < len(voisins):
                pile[-1] = (sommet, indice + 1)
                voisin = voisins[indice]
                if voisin not in vus:
                    vus.add(voisin)
                    pile.append((voisin, 0))
            else:
                fin.append(sommet)
                pile.pop()

    for station in graphe.stations:
        if station not in vus:
            visiter(station)

    vus.clear()
    composantes = []
    for depart in reversed(fin):
        if depart in vus:
            continue
        pile = [depart]
        vus.add(depart)
        comp = []
        while pile:
            sommet = pile.pop()
            comp.append(sommet)
            for voisin in transpose[sommet]:
                if voisin not in vus:
                    vus.add(voisin)
                    pile.append(voisin)
        composantes.append(sorted(comp))
    return composantes
