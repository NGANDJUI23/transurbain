"""Menu interactif et mise en forme des resultats."""

from __future__ import annotations

import json

from .flow import ford_fulkerson
from .graph import Graphe, charger, comparer_representations
from .journal import enregistrer
from .mst import kruskal, prim
from .shortest_paths import bellman_ford, centralite, dijkstra, existe_chemin, fermeture_transitive, reconstruire
from .traversal import (
    accessibles,
    composantes_connexes,
    composantes_fortement_connexes,
    est_connexe,
    parcours_bfs,
    parcours_dfs,
)

ALGORITHMES = (
    "dfs",
    "bfs",
    "accessibilite",
    "connexite",
    "cfc",
    "kruskal",
    "prim",
    "mst",
    "dijkstra",
    "bellman",
    "fermeture",
    "centralite",
    "flot",
    "perf",
)


def _n(nombre) -> str:
    if isinstance(nombre, float) and nombre.is_integer():
        return str(int(nombre))
    if isinstance(nombre, float):
        return f"{nombre:.3f}".rstrip("0").rstrip(".")
    return str(nombre)


def _groupe(composantes: list[list[str]]) -> str:
    return "\n".join("  {" + ", ".join(comp) + "}" for comp in composantes)


def _parcours(titre: str, graphe: Graphe, source: str, resultat: dict) -> str:
    ordre = " -> ".join(resultat["ordre"])
    liens = [f"  {fils} (depuis {pere})" for fils, pere in resultat["parents"].items() if pere]
    hors = [s for s in graphe.stations if s not in resultat["parents"]]
    texte = f"{titre}\nSource : {source}\nOrdre : {ordre}\nArbre :\n" + (
        "\n".join(liens) if liens else "  (aucun arc)"
    )
    if hors:
        texte += "\nNon atteints : " + ", ".join(hors)
    return texte


def _chemins(nom: str, graphe: Graphe, source: str, cible: str | None, critere: str, calcule) -> str:
    resultat = calcule(graphe, source, critere)
    lignes = [f"Algorithme : {nom}", f"Critere : {critere}", f"Source : {source}"]
    if resultat["cycle_negatif"]:
        lignes.append("Cycle de poids negatif atteignable : aucun plus court chemin fiable.")
        return "\n".join(lignes)
    if cible:
        chemin = reconstruire(resultat, source, cible)
        lignes.append(f"Cible : {cible}")
        if chemin is None:
            lignes.append("Aucun chemin.")
        else:
            lignes.append(f"Cout : {_n(resultat['distances'][cible])}")
            lignes.append("Chemin : " + " -> ".join(chemin))
        return "\n".join(lignes)
    lignes.append("Distances :")
    for station in graphe.stations:
        dist = resultat["distances"][station]
        valeur = "infini" if dist == float("inf") else _n(dist)
        lignes.append(f"  {station} : {valeur}")
    return "\n".join(lignes)


def _arbre(nom: str, arbre, connexe: bool) -> str:
    etat = "Le reseau non oriente est connexe." if connexe else (
        "Le reseau non oriente n'est pas connexe : foret couvrante."
    )
    aretes = "\n".join(f"  {a} - {b} ({_n(w)})" for a, b, w in arbre.aretes) or "  (aucune)"
    return f"Algorithme : {nom}\n{etat}\nCout total (distance) : {_n(arbre.cout)}\nLiaisons :\n{aretes}"


def executer(
    nom: str,
    graphe: Graphe,
    source: str | None = None,
    cible: str | None = None,
    critere: str = "distance",
    journaliser: bool = True,
) -> str:
    """Execute un algorithme et renvoie le texte du resultat."""
    if nom not in ALGORITHMES:
        raise ValueError(f"Algorithme inconnu : {nom}")

    def exiger_source() -> str:
        if not source:
            raise ValueError("Station source requise (--source)")
        if source not in graphe.index:
            raise ValueError(f"Station inconnue : {source}")
        return source

    if nom == "dfs":
        sommet = exiger_source()
        texte = _parcours("Parcours en profondeur (DFS)", graphe, sommet, parcours_dfs(graphe, sommet))
    elif nom == "bfs":
        sommet = exiger_source()
        texte = _parcours("Parcours en largeur (BFS)", graphe, sommet, parcours_bfs(graphe, sommet))
    elif nom == "accessibilite":
        sommet = exiger_source()
        atteints = set(accessibles(graphe, sommet))
        autres = [s for s in graphe.stations if s not in atteints]
        texte = (
            f"Accessibilite depuis {sommet}\n"
            f"Accessibles ({len(atteints)}) : {', '.join(sorted(atteints))}\n"
            f"Inaccessibles ({len(autres)}) : {', '.join(autres) if autres else 'aucune'}"
        )
    elif nom == "connexite":
        comps = composantes_connexes(graphe)
        etat = "connexe" if est_connexe(graphe) else "non connexe"
        texte = f"Reseau non oriente : {etat}\nComposantes ({len(comps)}) :\n{_groupe(comps)}"
    elif nom == "cfc":
        comps = composantes_fortement_connexes(graphe)
        texte = f"Composantes fortement connexes ({len(comps)}) :\n{_groupe(comps)}"
    elif nom == "kruskal":
        arbre, connexe = kruskal(graphe)
        texte = _arbre("Kruskal", arbre, connexe)
    elif nom == "prim":
        arbre, connexe = prim(graphe)
        texte = _arbre("Prim", arbre, connexe)
    elif nom == "mst":
        arbre_k, connexe_k = kruskal(graphe)
        arbre_p, connexe_p = prim(graphe)
        memes = abs(arbre_k.cout - arbre_p.cout) < 1e-9
        texte = (
            _arbre("Kruskal", arbre_k, connexe_k)
            + "\n\n"
            + _arbre("Prim", arbre_p, connexe_p)
            + "\n\n"
            + ("Meme cout total." if memes else "Couts differents.")
        )
    elif nom == "dijkstra":
        texte = _chemins("Moore-Dijkstra", graphe, exiger_source(), cible, critere, dijkstra)
    elif nom == "bellman":
        texte = _chemins("Bellman-Ford", graphe, exiger_source(), cible, critere, bellman_ford)
    elif nom == "fermeture":
        matrice = fermeture_transitive(graphe)
        n = graphe.nb_sommets()
        paires = sum(matrice[i][j] for i in range(n) for j in range(n) if i != j)
        lignes = [f"Fermeture transitive (Warshall)\nPaires reliees hors diagonale : {paires}"]
        if source and cible:
            if source not in graphe.index or cible not in graphe.index:
                raise ValueError("Station inconnue")
            ok = existe_chemin(graphe, source, cible)
            lignes.append(f"Chemin {source} -> {cible} : {'oui' if ok else 'non'}")
        if n <= 12:
            entete = "     " + " ".join(f"{s:>3}" for s in graphe.stations)
            lignes.append(entete)
            for i, station in enumerate(graphe.stations):
                cellules = " ".join(f"{'1' if matrice[i][j] else '.':>3}" for j in range(n))
                lignes.append(f"{station:>3}  {cellules}")
        texte = "\n".join(lignes)
    elif nom == "centralite":
        lignes = [f"Centralite harmonique (critere : {critere})", "Rang  Station  Score   Somme  Atteintes"]
        for rang, (station, score, total, atteints) in enumerate(centralite(graphe, critere), 1):
            lignes.append(f"{rang:>4}  {station:<7}  {score:.4f}  {_n(total):>5}  {atteints}")
        texte = "\n".join(lignes)
    elif nom == "flot":
        sommet = exiger_source()
        if not cible:
            raise ValueError("Station puits requise (--target)")
        if cible not in graphe.index:
            raise ValueError(f"Station inconnue : {cible}")
        resultat = ford_fulkerson(graphe, sommet, cible)
        chaines = "\n".join(
            f"  {i}. " + " -> ".join(chemin) + f"  (debit {_n(debit)})"
            for i, (chemin, debit) in enumerate(resultat["chaines"], 1)
        ) or "  (aucune)"
        coupe = "\n".join(
            f"  {a} -> {b} (capacite {_n(c)})" for a, b, c in resultat["coupe"]
        ) or "  (aucune)"
        texte = (
            f"Ford-Fulkerson\nSource : {sommet}\nPuits : {cible}\n"
            f"Flot maximum : {_n(resultat['valeur'])}\n"
            f"Chaines ameliorantes :\n{chaines}\n"
            f"Coupe minimale :\n{coupe}\n"
            f"Capacite de la coupe : {_n(resultat['capacite_coupe'])}\n"
            f"Goulets : "
            + (", ".join(f"{a}->{b}" for a, b, _c in resultat["coupe"]) or "aucun")
        )
    else:
        stats = comparer_representations(graphe)
        texte = (
            "Comparaison liste d'adjacence / matrice d'adjacence\n"
            f"Sommets : {stats['sommets']} | Arcs : {stats['arcs']} | Requetes : {stats['requetes']}\n"
            f"Memoire liste   : {stats['memoire_liste']} octets\n"
            f"Memoire matrice : {stats['memoire_matrice']} octets\n"
            f"Test d'arc liste    : {stats['temps_acces_liste']:.6f} s\n"
            f"Test d'arc matrice  : {stats['temps_acces_matrice']:.6f} s\n"
            f"Voisins liste       : {stats['temps_voisins_liste']:.6f} s\n"
            f"Voisins matrice     : {stats['temps_voisins_matrice']:.6f} s"
        )
    if journaliser:
        enregistrer(
            nom,
            {"source": source, "cible": cible, "critere": critere, "sommets": graphe.nb_sommets()},
            texte,
        )
    return texte


def saisir(message: str) -> str:
    try:
        texte = input(message).strip()
    except EOFError:
        print()
        raise SystemExit(0) from None
    if texte.lower() in {"q", "quitter"}:
        raise SystemExit(0)
    return texte


def saisir_station(graphe: Graphe, message: str) -> str:
    noms = ", ".join(graphe.stations)
    while True:
        valeur = saisir(f"{message} ({noms}) : ")
        if valeur in graphe.index:
            return valeur
        print("Station inconnue.")


def saisir_critere(defaut: str = "temps") -> str:
    while True:
        valeur = saisir(f"Critere [distance/temps/cout] (entree = {defaut}) : ") or defaut
        if valeur in ("distance", "temps", "cout"):
            return valeur
        print("Critere inconnu.")


def charger_dialogue() -> tuple[Graphe, str]:
    while True:
        chemin = saisir("Chemin du fichier reseau : ")
        try:
            return charger(chemin), chemin
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Erreur : {exc}")


def _montrer(texte: str, sortie: str | None) -> None:
    print()
    print(texte)
    print()
    if sortie:
        from pathlib import Path

        path = Path(sortie)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fichier:
            fichier.write(texte + "\n\n")


def menu(graphe: Graphe, nom_fichier: str, sortie: str | None = None) -> None:
    """Boucle du menu numerote. 0 revient en arriere, q quitte."""
    while True:
        print(
            "\n=== TransUrbain ===\n"
            f"Fichier : {nom_fichier}\n"
            f"Stations : {graphe.nb_sommets()} | Arcs : {graphe.nb_arcs()}\n"
            "1. Explorer le reseau\n"
            "2. Arbre couvrant minimum\n"
            "3. Plus courts chemins\n"
            "4. Flot maximum\n"
            "5. Comparer liste et matrice\n"
            "6. Charger un autre fichier\n"
            "0. Quitter\n"
            "q a n'importe quel prompt pour quitter"
        )
        choix = saisir("Choix : ")
        if choix == "0":
            return
        if choix == "1":
            _menu_exploration(graphe, sortie)
        elif choix == "2":
            _menu_arbre(graphe, sortie)
        elif choix == "3":
            _menu_chemins(graphe, sortie)
        elif choix == "4":
            source = saisir_station(graphe, "Source")
            cible = saisir_station(graphe, "Puits")
            _montrer(executer("flot", graphe, source, cible), sortie)
        elif choix == "5":
            _montrer(executer("perf", graphe), sortie)
        elif choix == "6":
            graphe, nom_fichier = charger_dialogue()
        else:
            print("Choix invalide.")


def _menu_exploration(graphe: Graphe, sortie: str | None) -> None:
    while True:
        print(
            "\nExploration\n"
            "1. DFS\n2. BFS\n3. Accessibilite depuis une station\n"
            "4. Composantes connexes\n5. Composantes fortement connexes\n0. Retour"
        )
        choix = saisir("Choix : ")
        if choix == "0":
            return
        if choix in {"1", "2", "3"}:
            source = saisir_station(graphe, "Station de depart")
            nom = {"1": "dfs", "2": "bfs", "3": "accessibilite"}[choix]
            _montrer(executer(nom, graphe, source), sortie)
        elif choix == "4":
            _montrer(executer("connexite", graphe), sortie)
        elif choix == "5":
            _montrer(executer("cfc", graphe), sortie)
        else:
            print("Choix invalide.")


def _menu_arbre(graphe: Graphe, sortie: str | None) -> None:
    while True:
        print("\nArbre couvrant (distance)\n1. Kruskal\n2. Prim\n3. Comparer Kruskal et Prim\n0. Retour")
        choix = saisir("Choix : ")
        if choix == "0":
            return
        nom = {"1": "kruskal", "2": "prim", "3": "mst"}.get(choix)
        if nom:
            _montrer(executer(nom, graphe), sortie)
        else:
            print("Choix invalide.")


def _menu_chemins(graphe: Graphe, sortie: str | None) -> None:
    while True:
        print(
            "\nPlus courts chemins\n"
            "1. Moore-Dijkstra\n2. Bellman-Ford\n3. Fermeture transitive\n"
            "4. Stations centrales\n0. Retour"
        )
        choix = saisir("Choix : ")
        if choix == "0":
            return
        if choix in {"1", "2"}:
            source = saisir_station(graphe, "Depart")
            cible = saisir("Arrivee (entree = toutes les stations) : ") or None
            if cible and cible not in graphe.index:
                print("Station inconnue.")
                continue
            critere = saisir_critere()
            nom = "dijkstra" if choix == "1" else "bellman"
            try:
                _montrer(executer(nom, graphe, source, cible, critere), sortie)
            except ValueError as exc:
                print(f"Erreur : {exc}")
        elif choix == "3":
            source = saisir("Depart (entree = matrice seule) : ") or None
            cible = saisir("Arrivee (entree = matrice seule) : ") or None
            try:
                _montrer(executer("fermeture", graphe, source, cible), sortie)
            except ValueError as exc:
                print(f"Erreur : {exc}")
        elif choix == "4":
            try:
                _montrer(executer("centralite", graphe, critere=saisir_critere()), sortie)
            except ValueError as exc:
                print(f"Erreur : {exc}")
        else:
            print("Choix invalide.")
