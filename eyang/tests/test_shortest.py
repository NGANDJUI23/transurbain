"""Plus courts chemins, Warshall et centralite."""

from pathlib import Path

import pytest

from src.graph import charger
from src.shortest_paths import bellman_ford, centralite, dijkstra, existe_chemin, reconstruire

DATA = Path(__file__).resolve().parents[1] / "data"


def test_dijkstra_distance(petit):
    resultat = dijkstra(petit, "A", "distance")
    assert reconstruire(resultat, "A", "F") == ["A", "C", "E", "D", "F"]
    assert resultat["distances"]["F"] == 8


def test_dijkstra_temps(petit):
    resultat = dijkstra(petit, "A", "temps")
    assert reconstruire(resultat, "A", "F") == ["A", "B", "D", "F"]
    assert resultat["distances"]["F"] == 7


def test_bellman_egal_dijkstra(petit):
    for critere in ("distance", "temps"):
        court = dijkstra(petit, "A", critere)["distances"]
        long = bellman_ford(petit, "A", critere)["distances"]
        assert court == long
        assert bellman_ford(petit, "A", critere)["cycle_negatif"] is False


def test_cycle_negatif():
    graphe = charger(DATA / "reseau_cycle_negatif.json")
    assert bellman_ford(graphe, "A", "cout")["cycle_negatif"] is True
    with pytest.raises(ValueError):
        dijkstra(graphe, "A", "cout")


def test_fermeture(petit):
    assert existe_chemin(petit, "A", "F")
    assert not existe_chemin(petit, "F", "A")
    assert not existe_chemin(petit, "C", "B")


def test_centralite(petit):
    rang = centralite(petit, "temps")
    assert {station for station, *_ in rang} == set(petit.stations)
    scores = [score for _, score, _, _ in rang]
    assert scores == sorted(scores, reverse=True)
