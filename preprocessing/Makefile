.ONESHELL:
SHELL := /bin/bash
PYTHON=python

ifdef sub
ARGS := -s ${sub} 
else
ARGS = 
endif

ifdef conf
ARGSS := -c ${conf} 
else
ARGSS = 
endif

help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  setup         create virtual environment and install dependencies"
	@echo "  preprocess    run preprocessing pipeline"
	@echo "  report    	   generate reports"

setup:
	$(PYTHON) -m venv env
	pip install requirements.txt
	$(shell mkdir -p $(DIRS))

convert:
	$(PYTHON) 00_convert_to_bids.py $(ARGS) $(ARGSS)
prepare_data:
	$(PYTHON) 01_prepare_data.py $(ARGS) $(ARGSS)
perform_ica:
	$(PYTHON) 02_perform_ica.py $(ARGS) $(ARGSS)
label_ics:
	$(PYTHON) 03_label_ics.py $(ARGS) $(ARGSS)
filter_and_clean:
	$(PYTHON) 04_filter_and_clean.py $(ARGS) $(ARGSS)
epoch_and_average:
	$(PYTHON) 05_epoch_and_average.py $(ARGS) $(ARGSS)
report:
	$(PYTHON) 91_report_subject.py $(ARGS) $(ARGSS)
preprocess:
	prepare_data
	perform_ica
	label_ics
	filter_and_clean
	epoch_and_average
run_full:
	preprocess
	report