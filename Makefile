PYTHON  ?= python3
INPUT   ?= data/reseau.json
OUTPUT  ?= resultats.txt
JOURNAL ?= journal.log

.PHONY: help install test run demo report clean lint

help:
	@echo "Cibles disponibles :"
	@echo "  make install   — installe les dépendances"
	@echo "  make test      — lance la suite de tests"
	@echo "  make run       — lance le programme en mode interactif"
	@echo "  make demo      — exécute une démonstration non interactive"
	@echo "  make report    — génère le rapport technique"
	@echo "  make clean     — supprime les artefacts"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -v tests/

run:
	$(PYTHON) main.py --input $(INPUT)

demo:
	$(PYTHON) main.py --input $(INPUT) --algorithm dijkstra --source A --output $(OUTPUT)
	$(PYTHON) main.py --input $(INPUT) --algorithm kruskal >> $(OUTPUT)
	$(PYTHON) main.py --input $(INPUT) --algorithm maxflow --source A --target F >> $(OUTPUT)

report: demo test
	@echo "# Rapport technique — TransUrbain" > rapport.md
	@echo "" >> rapport.md
	@echo "Généré le $$(date)" >> rapport.md
	@echo "" >> rapport.md
	@echo "## Résultats d'exécution" >> rapport.md
	@echo '```' >> rapport.md
	@cat $(OUTPUT) >> rapport.md
	@echo '```' >> rapport.md
	@echo "Rapport généré : rapport.md"

clean:
	rm -f $(OUTPUT) rapport.md $(JOURNAL)
	rm -rf .pytest_cache __pycache__ */__pycache__