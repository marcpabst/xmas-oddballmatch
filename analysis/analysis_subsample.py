from configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time
import pandas as pd
import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = load_configuration()

config["bids_root_path"] = "/nfs/user/mo808sujo/xmasoddballmatch-bids"
config["pipeline_name"] = "pipeline01"

def cronbachs_alpha(X):
    """
    X: ndarray (n_items * n_observations)
    """
    N = X.shape[0]
    corrs = np.corrcoef(X)

    r = 0
    return = (N * r) / (1 + (N - 1) * r)

    

@python_app
def analyis_subsample(id, config):
    import mne
    from autoreject import AutoReject
    import utils
    import sys
    import numpy as np
    import pandas as pd

    

    

    def get_mean_amplitudes(evokeds, window, picks = "all"):

        means = []
        if isinstance(evokeds, list):
            for i, evoked in enumerate(evokeds):
                evoked = evoked.copy().pick(picks)

                _window = np.arange(evoked.time_as_index(window[0]),
                                    evoked.time_as_index(window[1]))

                data = evoked.data[:, _window]
                mean = data.mean()
                means.append(mean)
        else:
            return get_mean_amplitudes([evokeds], window, picks)[0]

        return means


    nums = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200]
    N = 100
    peak_latency = 0.135
    cond1 = "random/standard"
    cond2 = "random/deviant"
    peak = 0.135
    peakwindow = (peak-0.025,peak+0.025)

    # Read file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

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
    config["use_autoreject"] = False
    if config["use_autoreject"] is not None and config["use_autoreject"]:
        print("Running AutoReject...")
        ar = AutoReject(verbose = False)
        ar.fit(epochs)
        epochs = ar.transform(epochs)
    elif config["diff_criterion"] is not None:
        epochs = epochs.drop_bad(config["diff_criterion"])

    mean_amplitudes = {}
    mean_amplitudes["id"] = []
    mean_amplitudes["num"] = [] 
    mean_amplitudes["run"] = [] 
    mean_amplitudes["amplitude_difference"] = [] 

    epochs1 = epochs[cond1]
    epochs2 = epochs[cond2]

    idx1 = list(range(len(epochs1)))
    idx2 = list(range(len(epochs2)))


    for n in range(N):
        
        np.random.shuffle(idx1)
        np.random.shuffle(idx2)

        for num in nums:
            evokeds = {cond: [] for cond in [cond1, cond2]}
            
            subsample_epochs1 = epochs1[idx1[:num]]
            subsample_epochs2 = epochs2[idx2[:num]]

            # average
            evokeds[cond1].append(subsample_epochs1.average())
            evokeds[cond2].append(subsample_epochs2.average())

            # calculate amplitude difference (effect estimate)
            diff_waves = [mne.combine_evoked([e1,e2], [1,-1]) for e1,e2 in zip(evokeds["random/standard"], evokeds["random/deviant"])]
            ma = get_mean_amplitudes(diff_waves, peakwindow, picks = ["FZ"]) 

            mean_amplitudes["id"].append(id) 
            mean_amplitudes["num"].append(num)
            mean_amplitudes["run"].append(n)
            mean_amplitudes["type"].append("full") 
            mean_amplitudes["amplitude_difference"].append(np.mean(ma))

            # split-half
            evokeds_h1 = {cond: [] for cond in [cond1, cond2]}
            evokeds_h2 = {cond: [] for cond in [cond1, cond2]}
            

            subsample_epochs1_h1 = epochs1[idx1[:num]][:num]
            subsample_epochs1_h2 = epochs1[idx1[:num]][num:]

            subsample_epochs2_h1 = epochs2[idx2[:num]][:num]
            subsample_epochs2_h2 = epochs2[idx2[:num]][num:]

            # average
            evokeds_h1[cond1].append(subsample_epochs1_h1.average())
            evokeds_h2[cond1].append(subsample_epochs1_h2.average())

            evokeds_h1[cond2].append(subsample_epochs2_h1.average())
            evokeds_h2[cond2].append(subsample_epochs2_h2.average())

            # calculate amplitude difference (effect estimate)
            diff_waves_h1 = [mne.combine_evoked([e1,e2], [1,-1]) for e1,e2 in zip(evokeds_h1["random/standard"], evokeds_h1["random/deviant"])]
            diff_waves_h2 = [mne.combine_evoked([e1,e2], [1,-1]) for e1,e2 in zip(evokeds_h2["random/standard"], evokeds_h2["random/deviant"])]

            ma_h1 = get_mean_amplitudes(diff_waves_h1, peakwindow, picks = ["FZ"]) 
            ma_h2 = get_mean_amplitudes(diff_waves_h2, peakwindow, picks = ["FZ"]) 

            mean_amplitudes["id"].append(id) 
            mean_amplitudes["num"].append(num)
            mean_amplitudes["run"].append(n)
            mean_amplitudes["type"].append("half_1") 
            mean_amplitudes["amplitude_difference"].append(np.mean(ma_h1))

            mean_amplitudes["id"].append(id) 
            mean_amplitudes["num"].append(num)
            mean_amplitudes["run"].append(n)
            mean_amplitudes["type"].append("half_2") 
            mean_amplitudes["amplitude_difference"].append(np.mean(ma_h2))




    return pd.DataFrame(mean_amplitudes)
   

def main():
    parsl.load(pconfig)
    ids = get_entity_vals(config["bids_root_path"], "sub")
    tasks = [analyis_subsample(id, config) for id in ids]
    #tasks = [analyis_subsample(id, config) for id in ["001"]]

    mean_amplitudes = [i.result() for i in tasks]

    df = pd.concat(mean_amplitudes)
    df.to_csv("out100.csv")
    print(df)


if __name__ == '__main__':
    main()