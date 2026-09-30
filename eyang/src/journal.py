"""Journal des executions, une ligne JSON par action."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

JOURNAL = Path(__file__).resolve().parents[1] / "logs" / "journal.txt"


def enregistrer(algorithme: str, parametres: dict, resume: str, chemin: Path | None = None) -> None:
    """Ajoute une action au journal."""
    destination = chemin or JOURNAL
    destination.parent.mkdir(parents=True, exist_ok=True)
    entree = {
        "horodatage": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "algorithme": algorithme,
        "parametres": parametres,
        "resume": resume[:2000],
    }
    with destination.open("a", encoding="utf-8") as fichier:
        fichier.write(json.dumps(entree, ensure_ascii=False) + "\n")
