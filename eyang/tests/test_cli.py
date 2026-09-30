"""Ligne de commande."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PYTHON = sys.executable


def _run(args):
    return subprocess.run(
        [PYTHON, str(ROOT / "main.py"), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_aide():
    proc = _run(["-h"])
    assert proc.returncode == 0
    assert "--input" in proc.stdout
    assert "--algorithm" in proc.stdout


def test_dijkstra_direct(tmp_path):
    sortie = tmp_path / "itineraire.txt"
    proc = _run(
        [
            "--input",
            str(DATA / "reseau_petit.json"),
            "--algorithm",
            "dijkstra",
            "--source",
            "A",
            "--target",
            "F",
            "--critere",
            "distance",
            "--output",
            str(sortie),
        ]
    )
    assert proc.returncode == 0, proc.stderr
    assert "A -> C -> E -> D -> F" in proc.stdout
    assert sortie.read_text(encoding="utf-8").count("A -> C -> E -> D -> F") == 1


def test_flot_direct():
    proc = _run(
        [
            "--input",
            str(DATA / "reseau_petit.csv"),
            "--format",
            "csv",
            "--algorithm",
            "flot",
            "--source",
            "A",
            "--target",
            "F",
        ]
    )
    assert proc.returncode == 0, proc.stderr
    assert "Flot maximum : 13" in proc.stdout


def test_source_manquante():
    proc = _run(
        ["--input", str(DATA / "reseau_petit.json"), "--algorithm", "dijkstra"]
    )
    assert proc.returncode == 1


def test_journal():
    journal = ROOT / "logs" / "journal.txt"
    avant = journal.read_text(encoding="utf-8") if journal.exists() else ""
    proc = _run(
        [
            "--input",
            str(DATA / "reseau_petit.json"),
            "--algorithm",
            "connexite",
        ]
    )
    assert proc.returncode == 0, proc.stderr
    ajoute = journal.read_text(encoding="utf-8")[len(avant) :]
    entree = json.loads(ajoute.strip().splitlines()[-1])
    assert entree["algorithme"] == "connexite"
