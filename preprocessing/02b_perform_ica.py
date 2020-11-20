from ...configuration.configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time

import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = None

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

    # Filter
    logging.getLogger('mne').info("Filtering.")
    raw = raw.filter(
        l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window=config["ica_fir_window"])

    # # Remove line noise using ZapLine
    # logging.getLogger('mne').info("Running ZapLine.")
    # raw = utils.apply_zapline(
    #         raw, config["line_freq"], picks=["eeg", "eog"], nremove=4)

    # # Running PREP
    # logging.getLogger('mne').info("Running PREP.")
    # prep_params = {
    #     "ref_chs": "eeg",
    #     "reref_chs": "eeg",
    #     "line_freqs": [],
    # }

    # prep = PrepPipeline(raw, prep_params, raw.get_montage())
    # prep.fit()

    # # Drop bad channels
    # raw.pick(exclude=rprep.interpolated_channels)

    #logging.getLogger('mne').info("{} bad channels (of {}) dropped.".format(n_bads, n_channels))

    # Run ASR
    logging.getLogger('mne').info("Run ASR.")
    raw.apply_function(utils.asr, channel_wise = False, sfreq = raw.info["sfreq"]) 
  
    # Create ICA
    ica = mne.preprocessing.ICA(method="picard", random_state=config["random_state"], max_iter=600)
    
    # Fit ICA
    logging.getLogger('mne').info("Runing ICA.")
    ica.fit(raw, picks="eeg")

    # Save ICA to disk
    logging.getLogger('mne').info("Saving ICA to disk.")
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")

    ica.save(ica_filename)


def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)
    parser.add_argument('-c', '--config', type=str,
                        help='Config file', required=True)

    args = parser.parse_args()
    config = load_configuration(args.config)
    
    parsl.load(pconfig)
    parsl.set_stream_logger()

    if args.subjects:
        tasks = [perform_ica(id, config) for id in args.subjects]
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        tasks = [perform_ica(id, config) for id in ids]

    while not all([i.done() for i in tasks]):
        time.sleep(1)
        r = sum([i.running() for i in tasks])
        f = sum([i.done() for i in tasks])
        c = sum([i.cancelled() for i in tasks])
        a = len(tasks)
        print("Task overview: {}/{}/{}/{} running/finished/canceled/all.".format(r,f,c,a))
        print(tasks[0].task_status())


if __name__ == '__main__':
    main()

