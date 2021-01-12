###########################################
########## Filter and clean data ##########
###########################################

from parsl.app.app import python_app


@python_app
def filter_and_clean(id, config, inputs=[]):

    import mne
    from autoreject import Ransac, AutoReject, get_rejection_threshold
    import utils
    import numpy as np
    from os.path import join
    import pandas as pd
    import logging
    import sys
    from interop2 import EEG, EEGlab
    from scipy.io import savemat

    # Logging
    log_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="log")
    sys.stdout = open(log_filename, 'w', buffering = 1)

    # Read file from disk
    input_pipeline_name = config.get("input_pipeline_name", config["pipeline_name"])
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, input_pipeline_name, ".fif", suffix="raw", processing="prepared")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, input_pipeline_name, ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload = True)
    events = mne.read_events(events_filename)

    # Channel names to upper case
    upper = lambda s: s.upper()
    raw.rename_channels(upper)

    # Read ICA and labels from disk
    if config["use_ica"]:
        ica_filename = utils.get_derivative_file_name(
            config["bids_root_path"], id, input_pipeline_name, ".fif", suffix="ica")
        ica = mne.preprocessing.read_ica(ica_filename)
        csv_filename = utils.get_derivative_file_name(
            config["bids_root_path"], id, input_pipeline_name, ".csv", suffix="ica-matlab")
        labels = pd.read_csv(csv_filename)

        labels_names = labels.idxmax(axis=1).tolist()
        labels_confidence = labels.max(axis=1).tolist()
        exclude_idx = [i for i, name in enumerate(labels_names) if name != "Brain" and name != "Other"]

    
        mne.channels.rename_channels(ica.info, upper)
        ica.ch_names = ica.info.ch_names

        # Annotate bad channels 
        raw.info["bads"] = list(set(raw.info["ch_names"]) -  set(ica.info["ch_names"]))

        # Assign correct channel types
        # raw = raw.set_channel_types(
        #     {"SO2": "eeg", "IO2": "eeg", "LO1": "eeg", "LO2": "eeg"})

        # Apply ICA to data, but zeroing-out non-brain components
        raw = ica.apply(raw, exclude=exclude_idx)

    # Interpolate bad channels
    raw.interpolate_bads(reset_bads = True)

    # Bipolarize EOG
    raw = mne.set_bipolar_reference(raw, "SO2", "IO2", "vEOG")
    raw = mne.set_bipolar_reference(raw, "LO1", "LO2", "hEOG")

    # Re-reference
    #raw = raw.set_eeg_reference(["Nose"])

    # Filter data
    if config["filter"] is not None:
        raw = raw.filter(l_freq = config["filter"]["l_freq"], h_freq = config["filter"]["h_freq"], fir_window = config["filter"]["fir_window"])
            
    # Write to file
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    raw.save(raw_filename, overwrite = True)
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    mne.write_events(events_filename, events)

