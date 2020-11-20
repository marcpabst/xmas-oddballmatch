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
	source env/bin/activate
	pip install requirements.txt
	$(shell mkdir -p $(DIRS))

convert:
	source env/bin/activate
	$(PYTHON) 00_convert_to_bids.py $(ARGS) $(ARGSS)
prepare_data:
	source env/bin/activate
	$(PYTHON) 01_prepare_data.py $(ARGS) $(ARGSS)
	deactivate
perform_ica:
	source env/bin/activate
	$(PYTHON) 02_perform_ica.py $(ARGS) $(ARGSS)
	deactivate
label_ics:
	source env/bin/activate
	$(PYTHON) 03_label_ics.py $(ARGS) $(ARGSS)
	deactivate
filter_and_clean:
	source env/bin/activate
	$(PYTHON) 04_filter_and_clean.py $(ARGS) $(ARGSS)
	deactivate
epoch_and_average:
	source env/bin/activate
	$(PYTHON) 05_epoch_and_average.py $(ARGS) $(ARGSS)
	deactivate
report:
	source env/bin/activate
	$(PYTHON) 91_report_subject.py $(ARGS) $(ARGSS)
	deactivate
preprocess:
	prepare_data
	perform_ica
	label_ics
	filter_and_clean
	epoch_and_average
run_full:
	preprocess
	report