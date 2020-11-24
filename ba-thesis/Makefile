.ONESHELL:
SHELL := /bin/bash

prepare:
	mkdir ./temp
	cp -r ./input/* ./temp
	for f in temp/*.md; do python3 substitute.py -y temp/vars.yaml -t $$f -o $$f; done
	
cleanup: 
	rm -rf ./temp

cpdf:
	cd ./temp
	pandoc *.md -s -o ../output/output.pdf  --from markdown+raw_attribute --pdf-engine=xelatex --bibliography=/home/marc/Documents/bib.json --csl ../templates/apa.csl --template ../templates/thesis
ctex:
	cd ./temp
	pandoc *.md -s -o ../output/output.tex  --from markdown+raw_attribute --pdf-engine=xelatex --bibliography=references.json --csl ../templates/apa.csl --template ../templates/thesis

pdf:	prepare cpdf cleanup

