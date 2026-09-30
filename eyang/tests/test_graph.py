"""Chargement et representations."""

from pathlib import Path

import pytest

from src.graph import charger

DATA = Path(__file__).resolve().parents[1] / "data"


def signature(graphe):
    arcs = [
        (a.source, a.destination, a.distance, a.temps, a.capacite, a.cout) for a in graphe.arcs
    ]
    return graphe.stations, arcs


def test_trois_formats_identiques():
    json_g = charger(DATA / "reseau_petit.json")
    csv_g = charger(DATA / "reseau_petit.csv")
    txt_g = charger(DATA / "reseau_petit.txt", "texte")
    assert signature(json_g) == signature(csv_g) == signature(txt_g)


def test_tabulations(tmp_path):
    fichier = tmp_path / "arcs.txt"
    fichier.write_text("# stations: A B\nA\tB\t1\t2\t3\n", encoding="utf-8")
    graphe = charger(fichier)
    assert graphe.poids("A", "B", "temps") == 2


def test_ligne_invalide(tmp_path):
    fichier = tmp_path / "mauvais.txt"
    fichier.write_text("A B foo 1 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        charger(fichier)


def test_arc_en_double(tmp_path):
    fichier = tmp_path / "double.txt"
    fichier.write_text("# stations: A B\nA B 1 1 1\nA B 2 2 2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        charger(fichier)


def test_station_absente(tmp_path):
    fichier = tmp_path / "absente.txt"
    fichier.write_text("# stations: A B\nA C 1 1 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        charger(fichier)


def test_fichier_absent():
    with pytest.raises(FileNotFoundError):
        charger(DATA / "inexistant.json")


def test_liste_et_matrice(petit):
    for source in petit.stations:
        assert petit.voisins(source, "liste") == petit.voisins(source, "matrice")
        for destination in petit.stations:
            assert petit.a_arc(source, destination, "liste") == petit.a_arc(
                source, destination, "matrice"
            )
