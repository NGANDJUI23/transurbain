# TransUrbain

Outil Python d'analyse d'un reseau de transport. Les algorithmes de graphes sont codes sans NetworkX, igraph ni graph-tool. NumPy sert uniquement aux matrices d'adjacence.

Le cout d'un arc, s'il n'est pas fourni, est egal a sa distance. Kruskal et Prim travaillent sur le reseau non oriente : entre deux stations, le poids est la plus petite distance des deux sens.

## Installation

Depuis ce dossier (`transurbain`) :

```text
python -m pip install -r requirements.txt
```

Python 3.10 ou plus recent est requis. Sur cette machine, l'environnement deja pret est :

```text
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Lancer

Menu interactif (demande le fichier, puis un menu numerote) :

```text
python main.py
```

Menu sur un fichier deja choisi :

```text
python main.py --input data/reseau_petit.json
```

Sans menu, un algorithme direct :

```text
python main.py --input data/reseau_petit.json --algorithm dijkstra --source A --target F --critere temps --output rapport/itineraire.txt
```

```text
python main.py --input data/reseau_petit.csv --format csv --algorithm flot --source A --target F
```

Options : `--input`, `--format` (`texte`, `json`, `csv`), `--algorithm`, `--source`, `--target`, `--critere` (`distance`, `temps`, `cout`), `--output`.

Dans le menu, `0` revient en arriere ou quitte, `q` quitte a n'importe quelle question. Chaque action est ajoutee a `logs/journal.txt`.

Algorithmes : `dfs`, `bfs`, `accessibilite`, `connexite`, `cfc`, `kruskal`, `prim`, `mst`, `dijkstra`, `bellman`, `fermeture`, `centralite`, `flot`, `perf`.

## Tester

```text
python -m pytest tests -q
```

Avec l'environnement du dossier parent :

```text
..\.venv\Scripts\python.exe -m pytest tests -q
```

Le `Makefile` automatise l'installation, les tests et le rapport :

```text
make install
make test
make rapport
make perf
```

`make` n'est pas installe par defaut sous Windows. S'il manque, les commandes `python` ci-dessus suffisent. `make rapport` regenere les fichiers de `rapport/`.

## Fichiers d'entree

Trois formats, memes informations.

Texte, une liaison par ligne (`source destination distance temps capacite`, cout optionnel en 6e colonne). Espaces ou tabulations. Les stations peuvent etre declarees :

```text
# stations: A B C D E F
A B 4 2 10
```

CSV avec en-tete `source,destination,distance,temps,capacite` (colonne `cout` optionnelle).

JSON :

```json
{
  "stations": ["A", "B"],
  "arcs": [
    {"source": "A", "destination": "B", "distance": 4, "temps": 2, "capacite": 10}
  ]
}
```

Jeux fournis :

| Fichier | Role |
|---|---|
| `data/reseau_petit.json` (aussi `.txt` et `.csv`) | 6 stations, resultats verifiables a la main |
| `data/reseau_non_connexe.txt` | deux composantes |
| `data/reseau_cycle_negatif.json` | cout negatif, pour Bellman-Ford |
| `data/reseau_moyen.json` | 20 stations |
| `data/reseau_grand.json` | 200 stations, comparaison memoire et temps |
