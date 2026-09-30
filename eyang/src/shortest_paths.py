"""Plus courts chemins, fermeture transitive et centralite."""

from __future__ import annotations

import heapq

from .graph import Graphe

INF = float("inf")


def _controle_critere(critere: str) -> None:
    if critere not in ("distance", "temps", "cout"):
        raise ValueError(f"Critere inconnu : {critere}")


def _chemin(parents: dict, source: str, cible: str, distances: dict) -> list[str] | None:
    if distances.get(cible, INF) == INF:
        return None
    chemin = []
    sommet = cible
    vus = set()
    while sommet is not None:
        if sommet in vus:
            return None
        vus.add(sommet)
        chemin.append(sommet)
        if sommet == source:
            chemin.reverse()
            return chemin
        sommet = parents.get(sommet)
    return None


def dijkstra(graphe: Graphe, source: str, critere: str = "distance") -> dict:
    """Moore-Dijkstra. Refuse un critere qui contient un poids negatif."""
    _controle_critere(critere)
    if source not in graphe.index:
        raise KeyError(source)
    for arc in graphe.arcs:
        if getattr(arc, critere) < 0:
            raise ValueError("Poids negatif : utilisez Bellman-Ford")
    distances = {station: INF for station in graphe.stations}
    distances[source] = 0.0
    parents: dict[str, str | None] = {source: None}
    tas = [(0.0, source)]
    fixes: set[str] = set()
    while tas:
        dist, sommet = heapq.heappop(tas)
        if sommet in fixes:
            continue
        fixes.add(sommet)
        for voisin in graphe.voisins(sommet):
            candidat = dist + graphe.poids(sommet, voisin, critere)
            if candidat < distances[voisin]:
                distances[voisin] = candidat
                parents[voisin] = sommet
                heapq.heappush(tas, (candidat, voisin))
    return {"distances": distances, "parents": parents, "cycle_negatif": False}


def bellman_ford(graphe: Graphe, source: str, critere: str = "distance") -> dict:
    """Bellman-Ford. Signale un cycle de poids negatif atteignable."""
    _controle_critere(critere)
    if source not in graphe.index:
        raise KeyError(source)
    arcs = [
        (arc.source, arc.destination, getattr(arc, critere))
        for arc in graphe.arcs
        if arc.source != arc.destination or getattr(arc, critere) < 0
    ]
    distances = {station: INF for station in graphe.stations}
    distances[source] = 0.0
    parents: dict[str, str | None] = {source: None}
    for _ in range(max(graphe.nb_sommets() - 1, 0)):
        modifie = False
        for origine, destination, poids in arcs:
            if distances[origine] == INF:
                continue
            candidat = distances[origine] + poids
            if candidat < distances[destination]:
                distances[destination] = candidat
                parents[destination] = origine
                modifie = True
        if not modifie:
            break
    cycle = False
    for origine, destination, poids in arcs:
        if distances[origine] < INF and distances[origine] + poids < distances[destination]:
            cycle = True
            break
    return {"distances": distances, "parents": parents, "cycle_negatif": cycle}


def reconstruire(resultat: dict, source: str, cible: str) -> list[str] | None:
    if resultat["cycle_negatif"]:
        return None
    return _chemin(resultat["parents"], source, cible, resultat["distances"])


def fermeture_transitive(graphe: Graphe) -> list[list[bool]]:
    """Matrice de Warshall : vrai s'il existe un chemin, longueur ignoree."""
    n = graphe.nb_sommets()
    matrice = [[False] * n for _ in range(n)]
    for i in range(n):
        matrice[i][i] = True
    for arc in graphe.arcs:
        matrice[graphe.index[arc.source]][graphe.index[arc.destination]] = True
    for k in range(n):
        colonne = [matrice[i][k] for i in range(n)]
        for i in range(n):
            if not colonne[i]:
                continue
            ligne_k = matrice[k]
            ligne_i = matrice[i]
            for j in range(n):
                if ligne_k[j]:
                    ligne_i[j] = True
    return matrice


def existe_chemin(graphe: Graphe, source: str, cible: str) -> bool:
    matrice = fermeture_transitive(graphe)
    return matrice[graphe.index[source]][graphe.index[cible]]


def centralite(graphe: Graphe, critere: str = "temps") -> list[tuple[str, float, float, int]]:
    """Centralite harmonique : somme des 1/distance vers les stations atteintes."""
    classement = []
    for source in graphe.stations:
        try:
            resultat = dijkstra(graphe, source, critere)
        except ValueError:
            resultat = bellman_ford(graphe, source, critere)
            if resultat["cycle_negatif"]:
                raise ValueError("Cycle negatif : centralite non definie") from None
        total = 0.0
        atteints = 0
        score = 0.0
        for station, dist in resultat["distances"].items():
            if station == source or dist == INF:
                continue
            total += dist
            atteints += 1
            score += INF if dist == 0 else 1.0 / dist
        classement.append((source, score, total, atteints))
    classement.sort(key=lambda ligne: (-ligne[1], ligne[0]))
    return classement
