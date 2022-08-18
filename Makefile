slides:
	make doc
	make clld

all:
	make map
	make doc
	make cldf
	make clld

cldf:
	cd data; cldfbench makecldf cldfbench_cariban_pronouns.py

clld:
	cd cp_clld; clld initdb development.ini

doc:
	cd docs/pld-slides; pylingdocs build

map:
	cd maps; python3 create_maps.py