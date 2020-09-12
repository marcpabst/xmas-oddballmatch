.ONESHELL:
SHELL := /bin/bash
PYTHON=python

ifdef sub
ARGS := -s ${sub} 
else
ARGS = 
endif

help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  setup         create virtual environment and install dependencies"
	@echo "  preprocess    run preprocessing pipeline"
	@echo "  statistics    generate statistics"
	@echo "  all           run full pipeline"

setup:
	$(PYTHON) -m venv env
	source env/bin/activate
	pip install requirements.txt
	$(shell mkdir -p $(DIRS))

convert:
	source env/bin/activate
	$(PYTHON) 00_convert_to_bids.py $(ARGS)

preprocess:
	source env/bin/activate
	$(PYTHON) 01_prepare_data.py $(ARGS)
	$(PYTHON) 02_perform_ica.py $(ARGS)
	$(PYTHON) 03_filter_and_epoch.py $(ARGS)
	$(PYTHON) 04_average_epochs.py $(ARGS)

report:
	source env/bin/activate
	$(PYTHON) 91_make_report_subject.py $(ARGS)