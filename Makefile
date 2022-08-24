slides:
	make docs
	make clld

pipe:
	make cldf
	make paradigms
	make slides

all:
	make maps
	make pipe
	make readme

.PHONY: data
data:
	make cldf
	make clld
	
cldf:
	cd data; cldfbench makecldf cldfbench_cariban_pronouns.py

clld:
	cd cp_clld; clld initdb development.ini

.PHONY: docs
docs:
	cd docs/pld-slides; pylingdocs build

.PHONY: maps
maps:
	cd maps; python3 create_maps.py

readme:
	cldf markdown data/cldf/Wordlist-metadata.json > data/cldf/README.md

paradigms:
	python3 scripts/pronoun_paradigms.py

bib:
	biblatex2bibtex /home/florianm/Dropbox/research/cariban/cariban_references.bib data/etc/cariban_references_out.bib