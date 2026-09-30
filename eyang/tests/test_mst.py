"""Kruskal et Prim."""

from pathlib import Path

from src.graph import charger
from src.mst import kruskal, prim

DATA = Path(__file__).resolve().parents[1] / "data"

ARETES = {("A", "C", 2), ("B", "C", 1), ("C", "E", 3), ("D", "E", 1), ("D", "F", 2)}


def _jeu(arbre):
    return {(a, b, int(w)) for a, b, w in arbre.aretes}


def test_kruskal_et_prim(petit):
    arbre_k, connexe_k = kruskal(petit)
    arbre_p, connexe_p = prim(petit)
    assert connexe_k and connexe_p
    assert arbre_k.cout == arbre_p.cout == 9
    assert arbre_k.nb_aretes == petit.nb_sommets() - 1
    assert _jeu(arbre_k) == _jeu(arbre_p) == ARETES


def test_foret_non_connexe():
    graphe = charger(DATA / "reseau_non_connexe.txt")
    arbre_k, connexe_k = kruskal(graphe)
    arbre_p, connexe_p = prim(graphe)
    assert not connexe_k and not connexe_p
    assert arbre_k.cout == arbre_p.cout == 4
    assert _jeu(arbre_k) == _jeu(arbre_p)
