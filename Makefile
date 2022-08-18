slides:
	make docs
	make clld

all:
	make maps
	make cldf
	make docs
	make clld
	make readme

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

