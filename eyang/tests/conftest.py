"""Configuration des tests."""

from pathlib import Path

import pytest

from src.graph import charger

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


@pytest.fixture
def petit():
    return charger(DATA / "reseau_petit.json")
