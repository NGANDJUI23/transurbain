"""Flot maximum par Ford-Fulkerson (chaine ameliorante choisie par BFS)."""

from __future__ import annotations

from collections import defaultdict, deque

from .graph import Graphe


def ford_fulkerson(graphe: Graphe, source: str, puits: str) -> dict:
    """Flot max, chaines ameliorantes et coupe minimale entre source et puits."""
    if source not in graphe.index or puits not in graphe.index:
        raise KeyError("Station inconnue")
    if source == puits:
        raise ValueError("La source et le puits doivent etre distincts")
    capacites = {(arc.source, arc.destination): arc.capacite for arc in graphe.arcs}
    flot = {cle: 0.0 for cle in capacites}
    ordre = list(capacites)

    def residuel(origine: str, destination: str) -> float:
        aller = capacites.get((origine, destination), 0.0) - flot.get((origine, destination), 0.0)
        retour = flot.get((destination, origine), 0.0)
        return aller + retour

    def voisins_residuels(origine: str) -> list[str]:
        candidats = []
        vus = set()
        for a, b in ordre:
            destination = b if a == origine else a if b == origine else None
            if destination is None or destination in vus:
                continue
            vus.add(destination)
            if residuel(origine, destination) > 1e-9:
                candidats.append(destination)
        return candidats

    chaines = []
    valeur = 0.0
    while True:
        parents: dict[str, str | None] = {source: None}
        file = deque([source])
        while file:
            sommet = file.popleft()
            for voisin in voisins_residuels(sommet):
                if voisin not in parents:
                    parents[voisin] = sommet
                    if voisin == puits:
                        file.clear()
                        break
                    file.append(voisin)
        if puits not in parents:
            break
        chemin = []
        sommet = puits
        while sommet is not None:
            chemin.append(sommet)
            sommet = parents[sommet]
        chemin.reverse()
        debit = min(residuel(chemin[i], chemin[i + 1]) for i in range(len(chemin) - 1))
        for i in range(len(chemin) - 1):
            origine, destination = chemin[i], chemin[i + 1]
            annule = min(debit, flot.get((destination, origine), 0.0))
            if annule:
                flot[(destination, origine)] -= annule
            reste = debit - annule
            if reste:
                flot[(origine, destination)] = flot.get((origine, destination), 0.0) + reste
        valeur += debit
        chaines.append((chemin, debit))

    atteints = {source}
    file = deque([source])
    while file:
        sommet = file.popleft()
        for voisin in voisins_residuels(sommet):
            if voisin not in atteints:
                atteints.add(voisin)
                file.append(voisin)
    coupe = []
    for arc in graphe.arcs:
        if arc.source in atteints and arc.destination not in atteints and arc.capacite > 0:
            coupe.append((arc.source, arc.destination, arc.capacite))
    return {
        "valeur": valeur,
        "chaines": chaines,
        "coupe": coupe,
        "capacite_coupe": sum(cap for _, _, cap in coupe),
        "source_coupe": sorted(atteints),
    }
