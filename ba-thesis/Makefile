.ONESHELL:
SHELL := /bin/bash

prepare:
	cp -r ./input/* ./temp
	for f in temp/*.md; do python3 substitute.py -y temp/vars.yaml -t $$f -o $$f; done

pdf: prepare
	cd ./temp
	pandoc *.md -s -o ../output/output.pdf  --from markdown+raw_attribute --pdf-engine=xelatex --bibliography=references.json --csl ../templates/apa.csl --template ../templates/thesis
tex: prepare
	cd ./temp
	pandoc *.md -s -o ../output/output.tex  --from markdown+raw_attribute --pdf-engine=xelatex --bibliography=references.json --csl ../templates/apa.csl --template ../templates/thesis

html:
	pandoc input/*.md -s -o output/output.html  --bibliography=input/references.json --csl templates/apa.csl
docx:
	pandoc input/*.md -s -o output/output.docx  --bibliography=input/references.json --csl templates/apa.csl --reference-doc templates/apa.docx

