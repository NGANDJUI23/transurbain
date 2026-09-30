"""Parcours, connexite, composantes fortement connexes."""

from pathlib import Path

from src.graph import charger
from src.traversal import (
    accessibles,
    composantes_connexes,
    composantes_fortement_connexes,
    est_connexe,
    parcours_bfs,
)

DATA = Path(__file__).resolve().parents[1] / "data"


def test_bfs_depuis_a(petit):
    assert parcours_bfs(petit, "A")["ordre"] == ["A", "B", "C", "D", "E", "F"]


def test_accessibilite(petit):
    assert set(accessibles(petit, "A")) == set(petit.stations)
    assert set(accessibles(petit, "F")) == {"D", "E", "F"}


def test_connexe(petit):
    assert est_connexe(petit)
    assert composantes_connexes(petit) == [["A", "B", "C", "D", "E", "F"]]


def test_non_connexe():
    graphe = charger(DATA / "reseau_non_connexe.txt")
    assert not est_connexe(graphe)
    assert composantes_connexes(graphe) == [["A", "B", "C"], ["D", "E"]]


def test_composantes_fortes(petit):
    composantes = {tuple(c) for c in composantes_fortement_connexes(petit)}
    assert composantes == {("A",), ("B",), ("C",), ("D", "E", "F")}
