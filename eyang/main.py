"""Point d'entree : ligne de commande et menu interactif."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.cli import ALGORITHMES, charger_dialogue, executer, menu
from src.graph import charger


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyse et optimisation d'un reseau de transport urbain."
    )
    parser.add_argument("--input", help="Fichier du reseau (texte, JSON ou CSV)")
    parser.add_argument("--format", choices=("texte", "json", "csv"), help="Format du fichier")
    parser.add_argument("--algorithm", choices=ALGORITHMES, help="Algorithme, sans menu")
    parser.add_argument("--source", help="Station source")
    parser.add_argument("--target", help="Station cible ou puits")
    parser.add_argument(
        "--critere",
        default="distance",
        choices=("distance", "temps", "cout"),
        help="Poids des plus courts chemins (defaut : distance)",
    )
    parser.add_argument("--output", help="Fichier ou ecrire le resultat")
    return parser


def main(argv: list[str] | None = None) -> int:
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    args = construire_parser().parse_args(argv)
    if not args.input:
        if args.algorithm:
            print("Precisez --input avec --algorithm.", file=sys.stderr)
            return 1
        print("=== TransUrbain ===")
        graphe, chemin = charger_dialogue()
        menu(graphe, chemin, args.output)
        return 0
    try:
        graphe = charger(args.input, args.format)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1
    if not args.algorithm:
        menu(graphe, args.input, args.output)
        return 0
    try:
        texte = executer(args.algorithm, graphe, args.source, args.target, args.critere)
    except (KeyError, ValueError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1
    print(texte)
    if args.output:
        destination = Path(args.output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(texte + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
