from configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = load_configuration()

@python_app
def prepare_data(id, config):
    import os 
    import logging
    import utils
    import socket

    logging.info("Starting on {}".format(socket.gethostname()))
    from joblib import Parallel, delayed
    from os.path import join
    from autoreject import Ransac, AutoReject
    import mne
    from mne_bids import make_bids_basename, read_raw_bids, write_raw_bids
    from mne_bids.utils import get_entity_vals

    # Read file from disk
    bids_basename = make_bids_basename(subject=id, task=config["task_name"])
    # read raw bids is problematic
    bids_filename = join(config["bids_root_path"], "sub-{}".format(id), "eeg", bids_basename + "_{}.bdf".format("eeg"))
    raw = mne.io.read_raw_bdf(bids_filename, preload=True)
    events = mne.find_events(raw, initial_event=True, shortest_event=1)

    # Include Only Channels of interest
    raw = raw.pick(config["include_channels"])

    # Drop EXG8
    raw = raw.drop_channels(["EXG8"])

    # Rename channels to match MNE's montage
    raw = raw.rename_channels(
        {"FZ": "Fz", "PZ": "Pz", "OZ": "Oz", "CZ": "Cz", "FP2": "Fp2"})

    # Re-Reference
    raw = raw.set_eeg_reference(["Nose"])

    # Assign correct channel types
    raw = raw.set_channel_types(
        {"SO2": "eog", "IO2": "eog", "LO1": "eog", "LO2": "eog", "Nose": "misc"})

    # Load and apply standard 10-20 montage
    #ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
    besa_montage = mne.channels.read_custom_montage("standard-10-5-cap385.elp")
    raw = raw.set_montage(besa_montage)
    

    # Write to file
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    raw.save(raw_filename, overwrite=True)
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    mne.write_events(events_filename, events)


def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    
    parsl.load(pconfig)
    parsl.set_stream_logger()

    if args.subjects:
        tasks = [prepare_data(id, config) for id in args.subjects]

    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        tasks = [prepare_data(id, config) for id in ids]

    [i.result() for i in tasks]


if __name__ == '__main__':
    main()
