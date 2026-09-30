#!/usr/bin/env python3
"""TransUrbain — point d'entrée.

Usage :
    python main.py --input mon_reseau.json
    python main.py --input mon_reseau.csv --algorithm dijkstra --source A --target D
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

from graph import Graph, compare_representations
from loader import load_graph
import exploration as exp
import mst as mst_mod
import shortest_paths as sp
import flows as fl


# ----------------------------- Journal -----------------------------
class Reporter:
    """Écrit à l'écran et, si demandé, dans un fichier de sortie."""

    def __init__(self, out_path: str | None = None) -> None:
        self.terminal = sys.stdout
        self.file = open(out_path, "w", encoding="utf-8") if out_path else None

    def write(self, msg: str = "") -> None:
        print(msg, file=self.terminal)
        if self.file:
            print(msg, file=self.file)

    def close(self) -> None:
        if self.file:
            self.file.close()


def setup_journal(path: str = "journal.log") -> None:
    logging.basicConfig(
        filename=path, level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        force=True,
    )


def log(action: str) -> None:
    logging.info(action)


# ----------------------------- Helpers -----------------------------
def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"{prompt}{suffix} : ").strip()
    return val or (default or "")


def ask_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        try:
            v = int(ask(prompt))
            if lo <= v <= hi:
                return v
        except (ValueError, KeyboardInterrupt):
            pass
        print(f"  ⚠ Entrez un nombre entre {lo} et {hi}.")


def print_graph_info(g: Graph, r: Reporter) -> None:
    r.write(f"\n=== Réseau chargé ===")
    r.write(f"  Type            : {'orienté' if g.directed else 'non orienté'}")
    r.write(f"  Stations        : {g.nb_vertices()}")
    r.write(f"  Liaisons        : {g.nb_edges()}")
    r.write(f"  Stations        : {', '.join(sorted(g.vertices))}")


# ----------------------------- Menus -----------------------------
def menu_exploration(g: Graph, r: Reporter) -> None:
    r.write("\n--- Exploration du réseau ---")
    r.write("  1. DFS depuis une station")
    r.write("  2. BFS depuis une station")
    r.write("  3. Stations accessibles depuis une station")
    r.write("  4. Composantes connexes (faibles)")
    r.write("  5. Composantes fortement connexes")
    r.write("  0. Retour")
    c = ask_int("Choix", 0, 5)
    if c == 0:
        return
    if c in (1, 2, 3):
        s = ask("Station de départ", g.vertices[0])
        if s not in g.adj:
            r.write("  ⚠ Station inconnue.")
            return
        if c == 1:
            r.write(f"  DFS : {' -> '.join(exp.dfs(g, s))}")
        elif c == 2:
            r.write(f"  BFS : {' -> '.join(exp.bfs(g, s))}")
        else:
            r.write(f"  Accessibles depuis {s} : {sorted(exp.reachable_from(g, s))}")
        log(f"exploration choix={c} source={s}")
    elif c == 4:
        comps = exp.weak_components(g)
        r.write(f"  {len(comps)} composante(s) connexe(s) :")
        for i, comp in enumerate(comps, 1):
            r.write(f"    C{i} ({len(comp)}) : {comp}")
        r.write(f"  Réseau connexe ? {'OUI' if len(comps) <= 1 else 'NON'}")
        log("composantes_faibles")
    else:
        comps = exp.strongly_connected_components(g)
        r.write(f"  {len(comps)} composante(s) fortement connexe(s) :")
        for i, comp in enumerate(comps, 1):
            r.write(f"    C{i} ({len(comp)}) : {comp}")
        log("composantes_fortes")


def menu_mst(g: Graph, r: Reporter) -> None:
    r.write("\n--- Arbre couvrant minimum ---")
    crit = ask("Critère (distance/time/capacity)", "distance")
    r.write("  1. Kruskal")
    r.write("  2. Prim")
    r.write("  3. Comparer les deux")
    r.write("  0. Retour")
    c = ask_int("Choix", 0, 3)
    if c == 0:
        return
    if c in (1, 3):
        m, tot = mst_mod.kruskal(g, crit)
        r.write(f"\n  Kruskal — poids total = {tot:.3f}")
        for u, v, w in m:
            r.write(f"    {u} -- {v}  ({w})")
    if c in (2, 3):
        start = ask("Sommet de départ pour Prim", g.vertices[0])
        m, tot = mst_mod.prim(g, crit, start)
        r.write(f"\n  Prim — poids total = {tot:.3f}")
        for u, v, w in m:
            r.write(f"    {u} -- {v}  ({w})")
    log(f"mst critere={crit} choix={c}")


def menu_shortest(g: Graph, r: Reporter) -> None:
    r.write("\n--- Plus courts chemins ---")
    r.write("  1. Dijkstra")
    r.write("  2. Bellman-Ford")
    r.write("  3. Fermeture transitive")
    r.write("  4. Stations les plus centrales")
    r.write("  0. Retour")
    c = ask_int("Choix", 0, 4)
    if c == 0:
        return
    crit = ask("Critère (distance/time)", "distance")
    if c in (1, 2):
        s = ask("Source", g.vertices[0])
        t = ask("Destination (vide = toutes)", "")
        algo = "dijkstra" if c == 1 else "bellman-ford"
        try:
            if t:
                d, path = sp.shortest_path(g, s, t, crit, algo)
                if d == sp.INF:
                    r.write(f"  Aucun chemin de {s} à {t}.")
                else:
                    r.write(f"  {' -> '.join(path)}  |  coût = {d:.3f}")
            else:
                dist, prev = (sp.dijkstra if c == 1 else sp.bellman_ford)(g, s, crit)
                for v in sorted(dist):
                    r.write(f"    {s} -> {v} : "
                            f"{'∞' if dist[v] == sp.INF else f'{dist[v]:.3f}'}")
        except ValueError as err:
            r.write(f"  ⚠ {err}")
    elif c == 3:
        cl = sp.transitive_closure(g)
        for v in sorted(cl):
            r.write(f"    {v} atteint : {sorted(cl[v])}")
    else:
        for v, tot in sp.centrality(g, crit)[:10]:
            r.write(f"    {v} : somme des distances = {tot:.3f}")


def menu_flows(g: Graph, r: Reporter) -> None:
    r.write("\n--- Flot maximum ---")
    s = ask("Station source", g.vertices[0])
    t = ask("Station puits", g.vertices[-1])
    try:
        value, flow, _, chains = fl.ford_fulkerson(g, s, t)
    except KeyError as err:
        r.write(f"  ⚠ {err}")
        return
    r.write(f"\n  Flot maximum {s} -> {t} : {value:.1f} passagers/h")
    r.write(f"  Nombre de chaînes améliorantes : {len(chains)}")
    for i, ch in enumerate(chains, 1):
        r.write(f"    chaîne {i} : {' -> '.join(ch)}")
    r.write("\n  Flots sur les arcs :")
    for (u, v), f in sorted(flow.items()):
        if f > 0:
            r.write(f"    {u} -> {v} : {f:.1f}")
    _, S, T, cut = fl.min_cut(g, s, t)
    r.write(f"\n  Coupe minimale : S = {sorted(S)} | T = {sorted(T)}")
    r.write(f"  Valeur de la coupe = {value:.1f}")
    r.write("  Arcs de la coupe (goulets d'étranglement) :")
    for u, v, c in cut:
        r.write(f"    {u} -> {v}  (capacité {c})")
    log(f"maxflow {s}->{t} valeur={value}")


def menu_representation(g: Graph, r: Reporter) -> None:
    r.write("\n--- Comparaison listes vs matrices ---")
    res = compare_representations(g)
    r.write(f"  Densité du graphe          : {res['densite']:.4f}")
    r.write(f"  Temps d'accès (listes)     : {res['temps_liste_s']*1000:.3f} ms")
    r.write(f"  Temps d'accès (matrices)   : {res['temps_matrice_s']*1000:.3f} ms")
    r.write(f"  Mémoire listes             : {res['memoire_liste_octets']} octets")
    r.write(f"  Mémoire matrice            : {res['memoire_matrice_octets']} octets")
    log("comparaison_representations")


def interactive_menu(g: Graph, r: Reporter) -> None:
    while True:
        r.write("\n" + "=" * 52)
        r.write("  TransUrbain — Menu principal")
        r.write("=" * 52)
        r.write("  1. Informations sur le réseau")
        r.write("  2. Exploration (DFS/BFS/composantes)")
        r.write("  3. Arbre couvrant minimum (Kruskal/Prim)")
        r.write("  4. Plus courts chemins")
        r.write("  5. Flot maximum / coupe minimale")
        r.write("  6. Comparer les représentations")
        r.write("  0. Quitter")
        c = ask_int("Votre choix", 0, 6)
        log(f"menu choix={c}")
        if c == 0:
            r.write("Au revoir.")
            return
        if c == 1:
            print_graph_info(g, r)
        elif c == 2:
            menu_exploration(g, r)
        elif c == 3:
            menu_mst(g, r)
        elif c == 4:
            menu_shortest(g, r)
        elif c == 5:
            menu_flows(g, r)
        elif c == 6:
            menu_representation(g, r)


# ------------------------- Exécution directe -------------------------
def run_direct(g: Graph, args, r: Reporter) -> None:
    algo = args.algorithm.lower()
    crit = args.criterion or "distance"
    if algo in ("dfs", "bfs"):
        s = args.source or g.vertices[0]
        out = exp.dfs(g, s) if algo == "dfs" else exp.bfs(g, s)
        r.write(" -> ".join(out))
    elif algo in ("components", "composantes"):
        for i, c in enumerate(exp.weak_components(g), 1):
            r.write(f"C{i} : {c}")
    elif algo in ("scc", "ccs"):
        for i, c in enumerate(exp.strongly_connected_components(g), 1):
            r.write(f"C{i} : {c}")
    elif algo == "kruskal":
        m, tot = mst_mod.kruskal(g, crit)
        r.write(f"Poids total = {tot}")
        for u, v, w in m:
            r.write(f"{u} -- {v} ({w})")
    elif algo == "prim":
        m, tot = mst_mod.prim(g, crit, args.source)
        r.write(f"Poids total = {tot}")
        for u, v, w in m:
            r.write(f"{u} -- {v} ({w})")
    elif algo in ("dijkstra", "bellman-ford"):
        s = args.source or g.vertices[0]
        d, prev = (sp.dijkstra if algo == "dijkstra" else sp.bellman_ford)(g, s, crit)
        if args.target:
            r.write(f"{' -> '.join(sp.build_path(prev, s, args.target))} "
                    f"| coût = {d[args.target]}")
        else:
            for v in sorted(d):
                r.write(f"{s} -> {v} : {d[v]}")
    elif algo in ("closure", "fermeture"):
        for v, s in sp.transitive_closure(g).items():
            r.write(f"{v} : {sorted(s)}")
    elif algo in ("maxflow", "flot"):
        if not args.source or not args.target:
            raise SystemExit("--source et --target requis pour maxflow.")
        val, flow, _, chains = fl.ford_fulkerson(g, args.source, args.target)
        r.write(f"Flot maximum = {val}")
        r.write(f"Chaînes améliorantes : {chains}")
    elif algo == "mincut":
        if not args.source or not args.target:
            raise SystemExit("--source et --target requis pour mincut.")
        val, S, T, cut = fl.min_cut(g, args.source, args.target)
        r.write(f"Valeur coupe = {val}")
        r.write(f"S = {sorted(S)}")
        r.write(f"T = {sorted(T)}")
        for u, v, c in cut:
            r.write(f"{u} -> {v} ({c})")
    elif algo == "compare":
        res = compare_representations(g)
        for k, v in res.items():
            r.write(f"{k} = {v}")
    else:
        raise SystemExit(f"Algorithme inconnu : {algo}")


# ------------------------------ main ------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="transurbain",
        description="Analyse et optimisation d'un réseau de transport urbain.",
    )
    p.add_argument("--input", "-i", help="Fichier d'entrée (TXT, JSON, CSV).")
    p.add_argument("--format", "-f", choices=["text", "json", "csv"], default=None)
    p.add_argument("--algorithm", "-a", default=None,
                   help="Exécution directe : dfs, bfs, components, scc, kruskal, "
                        "prim, dijkstra, bellman-ford, closure, maxflow, mincut, compare")
    p.add_argument("--source", "-s", default=None)
    p.add_argument("--target", "-t", default=None)
    p.add_argument("--criterion", "-c", choices=["distance", "time", "capacity"],
                   default="distance")
    p.add_argument("--output", "-o", default=None, help="Fichier de sortie.")
    p.add_argument("--journal", default="journal.log")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    setup_journal(args.journal)
    log(f"session démarrée | args={vars(args)}")
    r = Reporter(args.output)
    try:
        if not args.input:
            args.input = ask("Chemin du fichier d'entrée")
        g = load_graph(args.input, args.format)
        log(f"graphe chargé : {g}")
        print_graph_info(g, r)
        if args.algorithm:
            run_direct(g, args, r)
        else:
            interactive_menu(g, r)
    except FileNotFoundError as e:
        r.write(f"Erreur : {e}")
        return 2
    except Exception as e:  # noqa: BLE001
        logging.exception("Erreur")
        r.write(f"Erreur : {e}")
        return 1
    finally:
        r.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())