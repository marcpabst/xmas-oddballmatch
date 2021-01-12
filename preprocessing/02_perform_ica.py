from parsl.app.app import python_app


@python_app
def perform_ica(id, config, inputs=[]):
    import mne
    from mne_bids import make_bids_basename, read_raw_bids
    from mne_bids.utils import get_entity_vals
    from joblib import Parallel, delayed
    from autoreject import Ransac, AutoReject, get_rejection_threshold
    import utils
    from pyprep.prep_pipeline import PrepPipeline
    import numpy as np
    from os.path import join
    import logging
    import sys
    from interop2 import EEG, EEGlab
    from scipy.io import savemat

    # Logging
    log_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="log")
    sys.stdout = open(log_filename, 'w', buffering = 1)


    # Read File from Disk
    input_pipeline_name = config.get("input_pipeline_name", config["pipeline_name"])
    logging.getLogger('mne').info("Reading data from disk.")
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, input_pipeline_name, ".fif", suffix="raw", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, input_pipeline_name, ".txt", suffix="eve", processing="prepared")
    events = mne.read_events(events_filename)

    # Write files to new ppeline folder
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    raw.save(raw_filename, overwrite=True)
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    mne.write_events(events_filename, events)

    # Check if ICA is to be Used
    if not config["use_ica"]:
        logging.getLogger('mne').info("ICA Artefact Rejection not used.")
        return

    # Downsample
    logging.getLogger('mne').info("Downsampling for ICA.")
    raw = raw.resample(config["ica_downsample_freq"])

    # Filter for ICA
    logging.getLogger('mne').info("Filtering for ICA.")
    raw = raw.filter(
        l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window=config["ica_fir_window"])

    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")

    raw.pick(["eeg", "eog"])

    # ICA using EEEGLAB
    with EEGlab("preprocessing/eeglab", config["tmp_dir"]) as eeglab, EEG(inst=raw) as eeg:
        eeg = eeglab.perform_ica(eeg, csv_filename, eeglab.tmp_dir.name)
        savemat("tmp.mat", {"EEG": eeg.to_dict()})
        ica = eeg.get_ica()


    # Save ICA to disk
    logging.getLogger('mne').info("Saving ICA to disk.")
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")

    ica.save(ica_filename)