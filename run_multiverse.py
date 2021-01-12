#%%
import numpy as np
import itertools as it
import os
import sys
from pathlib import Path

import importlib
from mne_bids.utils import get_entity_vals

import parsl

from preprocessing.parsl_config import pconfig


# Import Preprocessing Functions
prepare_data = importlib.import_module("preprocessing.01_prepare_data").prepare_data
perform_ica = importlib.import_module("preprocessing.02_perform_ica").perform_ica
filter_and_clean = importlib.import_module("preprocessing.04_filter_and_clean").filter_and_clean
epoch_and_average = importlib.import_module("preprocessing.05_epoch_and_average").epoch_and_average

options = {
    'ICA': {'parameter_name': 'use_ica', 
        'levels': {
            'yes': True,
            'no': False}},
    'BaselineCorrection': {'parameter_name': 'baseline_window',
        'levels': {
            'yes': (-.1, 0), 
            'no': None}},
    'Filtering': {'parameter_name': 'filter', 
        'levels': {'None': None, 
            'Sussman': {'filter_method': 'firwin','fir_window': 'hamming','l_freq': 1,'h_freq': 30.0}, 
            'Widmann': {'filter_method': 'firwin','fir_window': 'hamming','l_freq': .1,'h_freq': 40.0,}}},
    'WindowWidth': {'parameter_name': 'window_width',
        'levels': {
            '25 ms': 0.025, 
            '50 ms': 0.050,
            '75 ms': 0.075}}
            }



def create_pipeline_name(config):
    config = {k:config[k] for k in sorted(config.keys())}
    name = "_".join([key.lower() + "-" + str(value).replace(" ", "").lower() for key, value in config.items()])
    
    return name

def create_prev_pipeline_name(config, curr):

    for c in curr:
        parameter_name = c
        config = {k:v for k,v in config.items() if k is not parameter_name}

    config = {k:config[k] for k in sorted(config.keys())}
    name = "_".join([key.lower() + "-" + str(value).replace(" ", "").lower() for key, value in config.items()])
    
    return name

def create_workflows(id, conf):
    workflow = []

    prefix = "multiverse"

    # Define Parameters used in each step
    steps = [[],["ICA"], ["Filtering"],["BaselineCorrection"]]
    # Define functions for each step
    step_function = [prepare_data, perform_ica, filter_and_clean, epoch_and_average]
   

    for n, (step, fct) in enumerate(zip(steps,step_function)):

        if n < 3:
            continue


        vars =  [item for sublist in steps[0:n+1] for item in sublist] 
 
        levels = [[{options[var]["parameter_name"]: level} for level in options[var]["levels"].values()] for var in vars]
        
        levels_hr = [[{var: level} for level in options[var]["levels"].keys()] for var in vars]
        
        combinations = it.product(*levels)
        combinations_hr = it.product(*levels_hr)

        next_inputs = []
        
        for comb, comb_hr in zip(combinations,combinations_hr):
            config = {k: v for d in comb for k, v in d.items()}
            config_hr = {k: v for d in comb_hr for k, v in d.items()}


            config["pipeline_name"] = prefix + "_" + create_pipeline_name(config_hr)
            config["input_pipeline_name"] = prefix + "_" + create_prev_pipeline_name(config_hr, step)
            
            #print(config["pipeline_name"])

            Path(os.path.join("/media/marc/Medien/machristine-bids", "derivatives", config["pipeline_name"])).mkdir(exist_ok=True)

            tmp_config = {**conf, **config}
            print(tmp_config["filter"])
            next_inputs.append(fct(id, tmp_config, inputs=workflow))
            # Call Function
            #print(" ", config["pipeline_name"])
        
        workflow = next_inputs

    return workflow




def run_step(config):

 
    parsl.load(pconfig)
    #parsl.set_stream_logger()

    ids = get_entity_vals(config["bids_root_path"], "sub")
    ids = ["001"]

    tasks = [e for s in [create_workflows(id, config) for id in ids] for e in s]


    return [i.result() for i in tasks]


from ruamel.yaml import YAML


def load_configuration(filename):
    # Load config
    yaml = YAML(typ='unsafe')

    with open(filename) as file:
        configuration = yaml.load(file.read())

    return configuration

config = load_configuration("configuration/multiverse_baseconfig.yml")

run_step(config)