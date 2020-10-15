from configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time

import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = load_configuration()

@python_app
def analyis_subsample(id, config):
    import mne
    from autoreject import AutoReject
    import utils
    import sys

    nums = [100, 200, 300, 400, 500]
    N = 10
    peak_latency = 0.135
    cond1 = "random/standard"
    cond2 = "random/deviant"

    # Read file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

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
        ar = AutoReject(verbose = False)
        ar.fit(epochs)
        epochs = ar.transform(epochs)
    elif config["diff_criterion"] is not None:
        epochs = epochs.drop_bad(config["diff_criterion"])

    mean_amplitudes = []

    for num in nums:
        for n in range(N):
            evokeds = {cond: [] for cond in [cond1, cond2]}
            
            for cond in [cond1, cond2]:
                # select epochs
                s_epochs = epochs[cond]

                # draw a random sample of epochs
                idx = list(range(len(s_epochs)))
                retain_idx = np.random.choice(idx, num)
                drop_idx = set(idx) - set(retain_idx)
                subsample_epochs = s_epochs.copy().drop(drop_idx)

                # apply autoreject
                subsample_epochs = ar.transform(subsample_epochs)
                # average
                evokeds[cond].append(subsample_epochs.average())

            # calculate amplitude differenc (effect estimate)
            diff_waves = [mne.combine_evoked([e1,e2], [1,-1]) for e1,e2 in zip(evokeds["random/standard"], evokeds["random/deviant"])]
            mean_amplitudes = get_mean_amplitudes(diff_waves, peakwindow, picks = ["FZ"]) 
            mean_amplitudes.append(mean(mean_amplitudes))

    return mean_amplitudes
   



def main():

    ids = get_entity_vals(config["bids_root_path"], "sub")
    #tasks = [epoch_and_average(id, config) for id in ids]
    tasks = [epoch_and_average(id, config) for id in ["001"]]

    mean_amplitudes = [i.result() for i in tasks]

    print(mean_amplitudes)


if __name__ == '__main__':
    main()