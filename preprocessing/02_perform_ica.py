from ...configuration.configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time

import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = load_configuration()

@python_app
def perform_ica(id, config):
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

    # Read file from disk
    logging.getLogger('mne').info("Reading data from disk.")
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

    # Downsample
    logging.getLogger('mne').info("Downsampling.")
    raw = raw.resample(config["ica_downsample_freq"])

    # Cut non-block data
    # raw = utils.cut_raw_blocks(
    #    raw, events, config["events_dict"], "begin", "end")

    # Filter
    logging.getLogger('mne').info("Filtering.")
    raw = raw.filter(
        l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window=config["ica_fir_window"])

    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")

    raw.pick(["eeg", "eog"])

    # ICA using EEEGLAB
    with EEGlab("./eeglab", config["tmp_dir"]) as eeglab, EEG(inst=raw) as eeg:
        eeg = eeglab.perform_ica(eeg, csv_filename, eeglab.tmp_dir.name)
        savemat("tmp.mat", {"EEG": eeg.to_dict()})
        ica = eeg.get_ica()


    # Save ICA to disk
    logging.getLogger('mne').info("Saving ICA to disk.")
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")

    ica.save(ica_filename)

def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    
    parsl.load(pconfig)
    parsl.set_stream_logger()

    if args.subjects:
        tasks = [perform_ica(id, config) for id in args.subjects]
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        tasks = [perform_ica(id, config) for id in ids]

    [i.result() for i in tasks]


if __name__ == '__main__':
    main()

