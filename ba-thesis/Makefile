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
	pandoc -F ../pandoc-crossref --citeproc  *.md -s -o ../output/output.pdf  --from markdown+raw_attribute --pdf-engine=xelatex --bibliography=/home/marc/Documents/bib.json --csl ../templates/apa.csl --template ../templates/thesis
ctex:
	cd ./temp
	pandoc -F ../pandoc-crossref --citeproc  *.md -s -o ../output/output.tex  --from markdown+raw_attribute --pdf-engine=xelatex --bibliography=references.json --csl ../templates/apa.csl --template ../templates/thesis
ctext:
	cd ./temp
	pandoc -F ../pandoc-crossref --citeproc  *.md  -o ../output/output.txt --bibliography=/home/marc/Documents/bib.json --csl ../templates/apa.csl
 
chtml:
	cd ./temp
	pandoc -F ../pandoc-crossref --citeproc  *.md  -o ../output/output.html --bibliography=/home/marc/Documents/bib.json --csl ../templates/apa.csl
 

pdf:	prepare cpdf cleanup
tex:	prepare ctex cleanup
text:	prepare ctext cleanup
html:	prepare chtml cleanup

