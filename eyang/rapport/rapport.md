# Rapport technique — reseau TransUrbain

## 1. Modele

Le reseau est un graphe oriente. Une station est un sommet. Une liaison est un arc avec une distance (km), un temps (minutes) et une capacite (passagers par heure). Le cout vaut la distance si le fichier ne le donne pas. Un cout negatif est accepte pour Bellman-Ford.

Les parcours, la fermeture transitive et les flots respectent le sens des arcs. La connexite faible et l'arbre couvrant ignorent le sens : s'il existe les deux sens, on garde la distance la plus petite. C'est le plan de liaison utile pour une maintenance ou une electrification.

## 2. Programme

`main.py` charge le fichier, verifie les nombres et les stations, puis ouvre le menu ou lance l'algorithme demande. Le code est reparti en modules : `graph`, `traversal`, `mst`, `shortest_paths`, `flow`, `cli`, `journal`. Aucune bibliotheque de graphes externe. Les deux representations (liste d'adjacence et matrices NumPy) sont construites au chargement. Les algorithmes parcourent la liste. La matrice sert a la comparaison de performances et existe pour chaque critere.

Les choix sont journalises dans `logs/journal.txt`, une ligne JSON par action.

## 3. Representations

Mesures sur 20 000 requetes. Les durees dependent de la machine.

| | Petit (6 stations, 10 arcs) | Grand (200 stations, 600 arcs) |
|---|---|---|
| Memoire liste | 2 652 octets | 183 176 octets |
| Memoire matrice | 1 188 octets | 1 320 000 octets |
| Test « l'arc existe-t-il ? » liste | 0,022 s | 0,022 s |
| Test « l'arc existe-t-il ? » matrice | 0,008 s | 0,009 s |
| Liste des voisins, liste | 0,005 s | 0,007 s |
| Liste des voisins, matrice | 0,024 s | 0,508 s |

Sur le petit reseau, la matrice occupe moins de place : un objet Python coute cher, et 6×6 nombres restent petits. Sur le grand reseau creux, la matrice en n² est environ sept fois plus lourde que la liste. Savoir si un arc existe est plus rapide en matrice (un acces). Lister les voisins est plus rapide en liste, et l'ecart devient net quand n grandit : la matrice relit toute la ligne.

## 4. Exploration

Reseau petit, non oriente : une seule composante, le reseau est connexe.

Sens des arcs conserve, composantes fortement connexes (Kosaraju) : {A}, {B}, {C}, {D, E, F}. On circule librement entre D, E et F. On ne revient pas vers A, B ou C.

Depuis A, BFS atteint A, B, C, D, E, F. Depuis F, seules D, E et F sont accessibles.

`data/reseau_non_connexe.txt` donne deux composantes : {A, B, C} et {D, E}.

## 5. Arbre couvrant minimum

Poids = distance. Kruskal et Prim donnent le meme cout.

Reseau petit, cout 9, liaisons B-C (1), D-E (1), A-C (2), D-F (2), C-E (3). C'est un arbre : 5 liaisons pour 6 stations.

Reseau moyen (20 stations) : les deux algorithmes donnent le cout 46. Le reseau est connexe.

Reseau non connexe : foret de cout 4. Le programme le signale au lieu d'inventer une liaison absente.

## 6. Plus courts chemins

De A vers F, les deux criteres ne choisissent pas le meme trajet.

| Critere | Algorithme | Cout | Chemin |
|---|---|---|---|
| distance | Dijkstra et Bellman-Ford | 8 | A → C → E → D → F |
| temps | Dijkstra | 7 | A → B → D → F |

Dijkstra refuse un poids negatif. Sur `reseau_cycle_negatif.json` (couts 1, -3, 1), Bellman-Ford signale un cycle negatif atteignable depuis A.

La fermeture transitive (Warshall) repond sans regarder la longueur. A atteint F. F n'atteint pas A. Sur le petit reseau, 18 paires de stations distinctes sont reliees par un chemin.

Centralite harmonique en temps : somme des inverses des temps de parcours vers les stations atteintes. Plus le score est grand, plus la station est centrale.

| Rang | Station | Score | Somme des temps | Stations atteintes |
|---|---|---|---|---|
| 1 | B | 1,87 | 12 | 4 |
| 2 | A | 1,38 | 22 | 5 |
| 3 | E | 1,33 | 4 | 2 |
| 4 | C | 1,03 | 10 | 3 |
| 5 | F | 0,83 | 5 | 2 |
| 6 | D | 0,75 | 6 | 2 |

B est la plus centrale pour le temps : elle rejoint vite une grande partie du reseau. A atteint tout le monde, mais certains trajets sont longs, donc son score est plus bas.

Itineraire le plus rapide sur le reseau moyen, de S000 a S010 : S000 → S004 → S008 → S010, en 11 minutes.

## 7. Flot maximum

De A vers F, Ford-Fulkerson (chaine ameliorante choisie par un parcours en largeur) donne un flot de 13 passagers par heure.

Chaines :

1. A → B → D → F, debit 7
2. A → C → E → F, debit 5
3. A → C → E → D → F, debit 1

La coupe minimale vaut aussi 13. Les goulets sont B → D (capacite 7) et C → E (capacite 6). Augmenter l'un de ces deux arcs augmente le debit entre A et F.

## 8. Complexites

n stations, m arcs.

| Algorithme | Complexite |
|---|---|
| BFS, DFS | O(n + m) |
| Kosaraju | O(n + m) |
| Kruskal | O(m log m) |
| Prim avec tas | O(m log n) |
| Dijkstra avec tas | O(m log n) |
| Bellman-Ford | O(n · m) |
| Warshall | O(n³) |
| Ford-Fulkerson par BFS | O(n · m²) |

## 9. Limites

Le temps d'un arc ne depend pas de l'affluence. Il n'y a pas de correspondance a pied entre stations. L'arbre couvrant ne respecte pas le sens de circulation : il decrit l'infrastructure, pas un itineraire. Un cycle de cout negatif rend les plus courts chemins indefinissables, et le programme le dit au lieu de renvoyer un trajet.
