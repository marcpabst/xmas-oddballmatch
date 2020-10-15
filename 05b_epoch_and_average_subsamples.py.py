###########################################
########## Filter and clean data ##########
###########################################

from configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time

import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = load_configuration()

@python_app
def epoch_and_average(id, config):
    import mne
    from autoreject import AutoReject
    import utils
    import numpy as np
    import sys

    # Read file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

    # Logging
    log_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="log")
    sys.stdout = open(log_filename, 'w', buffering = 1)

    # Interpolate bad channels (if we use autoreject, we interpolate after epoching)
    # raw.interpolate_bads(reset_bads = True)

    # Epoch data
    raw.pick(["eeg", "eog"])
    epochs = mne.Epochs(raw, events, config["events_dict"],
                        tmin=config["epoch_window"][0],
                        tmax=config["epoch_window"][1],
                        baseline=config["baseline_winow"],
                        #reject=config["diff_criterion"],
                        reject=None,
                        preload=True)

    raw = raw.set_channel_types(
        {"vEOG": "eog", "hEOG": "eog"})


    if config["use_autoreject"] is not None and config["use_autoreject"]:

        print("Running AutoReject...")
        # Use AutoReject to find optimal thresholds on the complete dataset. 
        # Later, we can apply those thresholds to our subset data
        ar = AutoReject(verbose = False)
        ar.fit(epochs)
    elif config["diff_criterion"] is not None:
        epochs = epochs.drop_bad(config["diff_criterion"])

    nums = [100, 200, 300, 400, 500]
    N = 10

    for i, num in enumerate(nums):
        for n in N:
            for cond in ["random/standard", "random/deviant"]:
                # select epochs
                s_epochs = epochs[cond]

                # draw a random sample of epochs
                idx = list(range(len(s_epochs)))
                retain_idx = np.random.choice(idx, num)
                drop_idx = set(idx) - set(retain_idx)
                subsample_epochs = s_epochs.copy().drop(drop_idx)

                # fit autoreject
                subsample_epochs = ar.transform(subsample_epochs)
                # average
                evoked = subsample_epochs.average()
            # compare
            # calculate amplitude differenc (effect estimate)
            # calculate p-value
            # store value somewhere


    evokeds_list = []
    for condition in config["conditions_of_interest"]:
        evoked = epochs[condition].average()
        evoked.comment = condition
        evokeds_list.append(evoked)

    ave_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave")

    mne.write_evokeds(ave_filename, evokeds_list)



def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    
    parsl.load(pconfig)
    parsl.set_stream_logger()

    if args.subjects:
        tasks = [epoch_and_average(id, config) for id in args.subjects]
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        tasks = [epoch_and_average(id, config) for id in ids]

    [i.result() for i in tasks]


if __name__ == '__main__':
    main()

