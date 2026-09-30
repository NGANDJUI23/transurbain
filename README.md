# TransUrbain — Analyse et optimisation d'un réseau de transport urbain

Outil logiciel en Python permettant d'analyser, d'optimiser et de simuler
un réseau de transport urbain modélisé par un graphe orienté pondéré.

Le projet couvre quatre modules complémentaires :

1. **Représentation et exploration** du réseau (listes / matrices, DFS, BFS, composantes)
2. **Arbres couvrants minimum** (Kruskal, Prim)
3. **Plus courts chemins** (Dijkstra, Bellman-Ford, fermeture transitive)
4. **Flots dans les réseaux** (Ford-Fulkerson, coupe minimale)

---

## Table des matières

- [Caractéristiques](#caractéristiques)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Structure du projet](#structure-du-projet)
- [Format des données d'entrée](#format-des-données-dentrée)
- [Utilisation](#utilisation)
  - [Mode interactif](#mode-interactif)
  - [Mode ligne de commande](#mode-ligne-de-commande)
- [Algorithmes implémentés](#algorithmes-implémentés)
- [Exemples](#exemples)
- [Tests](#tests)
- [Journal d'exécution](#journal-dexécution)
- [Makefile](#makefile)
- [Contraintes techniques](#contraintes-techniques)
- [Auteur](#auteur)

---

## Caractéristiques

- 100 % Python 3.10+, **sans bibliothèque externe de théorie des graphes**
  (pas de NetworkX, igraph, graph-tool)
- Utilisation autorisée de `NumPy` et de la bibliothèque standard
- Deux représentations en mémoire : **listes d'adjacence** et **matrices d'adjacence**
- Trois formats d'entrée supportés : **TXT**, **JSON**, **CSV**
- Menu interactif **numéroté** avec retour et sortie à tout moment
- **Journal d'exécution** horodaté (`journal.log`) pour reproductibilité
- CLI complète avec options `--input`, `--format`, `--algorithm`, `--source`,
  `--target`, `--criterion`, `--output`, `--journal`
- Suite de **tests unitaires** (`pytest`) couvrant chaque module
- **Makefile** pour automatiser installation, tests, démonstration et rapport

---

## Prérequis

| Élément        | Version minimale |
|----------------|------------------|
| Python         | 3.10             |
| pip            | 22               |
| NumPy          | 1.24             |
| pytest         | 7.0              |

---

## Installation

### 1. Cloner ou extraire le projet

```bash
cd transurbain
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python3 -m venv .venv
source .venv/bin/activate         # Linux / macOS
# .venv\Scripts\activate          # Windows
```

### 3. Installer les dépendances

```bash
make install
```

ou manuellement :

```bash
pip install -r requirements.txt
```

---

## Structure du projet

```
transurbain/
├── Makefile                # Automatisation (install, test, run, demo, report)
├── README.md               # Ce fichier
├── requirements.txt        # Dépendances (numpy, pytest)
├── main.py                 # Point d'entrée CLI + menu interactif
├── graph.py                # Module 1 : représentation (listes + matrices)
├── loader.py               # Chargement TXT / JSON / CSV + validation
├── exploration.py          # Module 1 : DFS, BFS, composantes, CCS
├── mst.py                  # Module 2 : Kruskal, Prim
├── shortest_paths.py       # Module 3 : Dijkstra, Bellman-Ford, fermeture
├── flows.py                # Module 4 : Ford-Fulkerson, coupe minimale
├── data/
│   ├── reseau.json         # Exemple JSON
│   ├── reseau.csv          # Exemple CSV
│   └── reseau.txt          # Exemple TXT
└── tests/
    ├── test_graph.py
    ├── test_exploration.py
    ├── test_mst.py
    ├── test_shortest_paths.py
    └── test_flows.py
```

---

## Format des données d'entrée

### Structure minimale attendue

- une **liste de sommets** identifiés par un nom ou un identifiant
- une **liste d'arcs** sous la forme `(source, destination, poids)`
  ou `(source, destination, poids, capacité)`

### Format JSON

```json
{
  "directed": true,
  "vertices": ["A", "B", "C", "D"],
  "arcs": [
    {"source": "A", "target": "B", "distance": 4, "time": 6, "capacity": 100},
    {"source": "B", "target": "C", "distance": 5, "time": 4, "capacity": 50}
  ]
}
```

Champs acceptés pour chaque arc (alias courants) :

| Champ      | Alias reconnus                    | Défaut       |
|------------|-----------------------------------|--------------|
| `source`   | `src`, `from`                     | — (requis)   |
| `target`   | `dst`, `to`, `destination`        | — (requis)   |
| `distance` | `weight`, `poids`                 | 1.0          |
| `time`     | `temps`                           | = `distance` |
| `capacity` | `capacite`                        | 0.0          |

### Format CSV

```csv
source,target,distance,time,capacity
A,B,4,6,100
A,C,2,3,80
B,C,5,4,50
```

L'en-tête doit être explicite (au moins `source` et `target`).

### Format TXT (tabulaire)

```
# Commentaire ignoré
A B 4 6 100
A C 2 3 80
B C 5 4 50
```

Colonnes séparées par espace ou tabulation :
`source target [distance] [time] [capacity]`.
Les lignes commençant par `#` sont ignorées.

---

## Utilisation

### Mode interactif

Lancement sans option d'algorithme :

```bash
python main.py --input data/reseau.json
```

ou simplement :

```bash
make run
```

Le programme affiche un menu numéroté :

```
====================================================
  TransUrbain — Menu principal
====================================================
  1. Informations sur le réseau
  2. Exploration (DFS/BFS/composantes)
  3. Arbre couvrant minimum (Kruskal/Prim)
  4. Plus courts chemins
  5. Flot maximum / coupe minimale
  6. Comparer les représentations
  0. Quitter
```

Chaque sous-menu propose un retour (`0`) et l'utilisateur peut
saisir les paramètres (station source, puits, critère de poids, etc.).

### Mode ligne de commande

Exécution directe d'un algorithme, sans passer par le menu :

```bash
python main.py --input <fichier> --algorithm <algo> [options]
```

Options disponibles :

| Option           | Description                                                    |
|------------------|----------------------------------------------------------------|
| `--input`, `-i`  | Fichier d'entrée (TXT, JSON, CSV)                              |
| `--format`, `-f` | Format explicite : `text`, `json`, `csv`                       |
| `--algorithm`,`-a`| Algorithme à exécuter (voir ci-dessous)                       |
| `--source`, `-s` | Sommet source                                                  |
| `--target`, `-t` | Sommet puits / destination                                     |
| `--criterion`,`-c`| Critère de poids : `distance`, `time`, `capacity`             |
| `--output`, `-o` | Fichier de sortie (redirection des résultats)                  |
| `--journal`      | Chemin du journal d'exécution (défaut : `journal.log`)         |

Valeurs acceptées pour `--algorithm` :

| Algorithme       | Description                                   |
|------------------|-----------------------------------------------|
| `dfs`            | Parcours en profondeur                        |
| `bfs`            | Parcours en largeur                           |
| `components`     | Composantes connexes (faibles)                |
| `scc`            | Composantes fortement connexes                |
| `kruskal`        | Arbre couvrant minimum (Kruskal)              |
| `prim`           | Arbre couvrant minimum (Prim)                 |
| `dijkstra`       | Plus court chemin (poids ≥ 0)                 |
| `bellman-ford`   | Plus court chemin (poids généraux)            |
| `closure`        | Fermeture transitive                          |
| `maxflow`        | Flot maximum entre source et puits            |
| `mincut`         | Coupe minimale                                |
| `compare`        | Comparaison listes vs matrices                |

---

## Algorithmes implémentés

| Module | Algorithmes                                                 |
|--------|-------------------------------------------------------------|
| 1      | DFS itératif, BFS, composantes connexes, Kosaraju (CCS)     |
| 2      | Kruskal (union-find), Prim (tas binaire)                    |
| 3      | Dijkstra (tas binaire), Bellman-Ford, fermeture transitive  |
| 4      | Ford-Fulkerson / Edmonds-Karp, coupe minimale               |

---

## Exemples

### Plus court chemin en distance

```bash
python main.py -i data/reseau.json -a dijkstra -s A -t F -c distance
```

Sortie :

```
A -> C -> E -> F  |  coût = 13.000
```

### Itinéraire le plus rapide

```bash
python main.py -i data/reseau.json -a dijkstra -s A -t F -c time
```

### Arbre couvrant minimum (électrification)

```bash
python main.py -i data/reseau.csv -a kruskal -c distance
```

### Flot maximum aux heures de pointe

```bash
python main.py -i data/reseau.json -a maxflow -s A -t F -o resultats.txt
```

### Coupe minimale (goulets d'étranglement)

```bash
python main.py -i data/reseau.json -a mincut -s A -t F
```

### Comparaison des représentations

```bash
python main.py -i data/reseau.txt -a compare
```

---

## Tests

Lancer la suite complète :

```bash
make test
```

ou directement :

```bash
pytest -v tests/
```

Couverture :

| Fichier                       | Ce qui est testé                                      |
|-------------------------------|-------------------------------------------------------|
| `test_graph.py`               | Matrice d'adjacence, graphe inversé                   |
| `test_exploration.py`         | DFS, BFS, composantes faibles et fortement connexes   |
| `test_mst.py`                 | Cohérence Kruskal / Prim, nombre d'arêtes             |
| `test_shortest_paths.py`      | Dijkstra, Bellman-Ford, cycles négatifs, fermeture    |
| `test_flows.py`               | Flot max, coupe min, théorème max-flot/min-coupe      |

---

## Journal d'exécution

Toutes les sessions sont enregistrées dans `journal.log` (horodaté).
Cela permet de :

- **reproduire** une session complète
- **comparer** plusieurs exécutions
- **auditer** les choix de l'utilisateur

Exemple de contenu :

```
2025-01-15 10:23:41,120 | INFO | session démarrée | args={...}
2025-01-15 10:23:41,145 | INFO | graphe chargé : Graph(orienté, 6 sommets, 8 arcs)
2025-01-15 10:23:52,031 | INFO | menu choix=4
2025-01-15 10:24:01,882 | INFO | maxflow A->F valeur=130.0
```

Changer le chemin du journal :

```bash
python main.py --input data/reseau.json --journal ma_session.log
```

---

## Makefile

| Cible           | Effet                                                       |
|-----------------|-------------------------------------------------------------|
| `make help`     | Affiche l'aide                                              |
| `make install`  | Installe les dépendances                                    |
| `make test`     | Lance la suite de tests                                     |
| `make run`      | Mode interactif                                             |
| `make demo`     | Démonstration non interactive                               |
| `make report`   | Génère `rapport.md` à partir des résultats et tests         |
| `make clean`    | Supprime les artefacts (`__pycache__`, journaux, rapport)   |

Variables surchargeables :

```bash
make run INPUT=data/mon_reseau.csv
make demo INPUT=data/mon_reseau.json OUTPUT=resultats.txt
```

---

## Contraintes techniques

- **Python 3.10 ou supérieur**
- **Aucune bibliothèque externe de théorie des graphes**
  (NetworkX, igraph, graph-tool interdits)
- `NumPy` et bibliothèque standard autorisés
- Code **modulaire**, **documenté** (docstrings) et **testé**
- Fichiers d'entrée fournis en TXT et JSON, structure documentée

---

## Auteur

Projet réalisé dans le cadre du module
**« Programmation : Analyse et optimisation d'un réseau de transport urbain »**.

Pour toute question : ouvrir une *issue* ou contacter l'enseignant responsable.