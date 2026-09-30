PYTHON ?= python

.PHONY: install test rapport perf

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest tests -q

perf:
	$(PYTHON) main.py --input data/reseau_grand.json --algorithm perf --output rapport/perf.txt

rapport:
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm connexite --output rapport/connexite.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm cfc --output rapport/cfc.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm kruskal --output rapport/kruskal.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm prim --output rapport/prim.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm mst --output rapport/mst.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm dijkstra --source A --target F --critere distance --output rapport/dijkstra_distance.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm dijkstra --source A --target F --critere temps --output rapport/dijkstra_temps.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm bellman --source A --target F --critere distance --output rapport/bellman.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm fermeture --source A --target F --output rapport/fermeture.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm centralite --critere temps --output rapport/centralite.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm flot --source A --target F --output rapport/flot.txt
	$(PYTHON) main.py --input data/reseau_non_connexe.txt --algorithm connexite --output rapport/non_connexe.txt
	$(PYTHON) main.py --input data/reseau_cycle_negatif.json --algorithm bellman --source A --critere cout --output rapport/cycle_negatif.txt
	$(PYTHON) main.py --input data/reseau_moyen.json --algorithm mst --output rapport/mst_moyen.txt
	$(PYTHON) main.py --input data/reseau_moyen.json --algorithm dijkstra --source S000 --target S010 --critere temps --output rapport/itineraire_moyen.txt
	$(PYTHON) main.py --input data/reseau_petit.json --algorithm perf --output rapport/perf_petit.txt
	$(PYTHON) main.py --input data/reseau_grand.json --algorithm perf --output rapport/perf.txt
