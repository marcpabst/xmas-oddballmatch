from configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time
import pandas as pd
#import parsl
#from parsl.app.app import python_app
#from parsl_config import pconfig

config = load_configuration("../configuration/pipeline01_100.yml")
config["100"] = {}
config["100"]["bids_root_path"] = "/nfs/user/mo808sujo/xmasoddballmatch-bids"
config["100"]["pipeline_name"] = "pipeline01"

config["150"] = {}
config["150"]["bids_root_path"] = "/nfs/user/mo808sujo/machristine-bids"
config["150"]["pipeline_name"] = "pipeline_christine"



def analyis_subsample(id, config, soa):
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


    #nums = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, ]
    nums = list(range(100, 3100, 100))
    N = 100
    peak_latency = 0.138
    cond1 = "random/standard"
    cond2 = "random/deviant"
    peak = 0.138
    peakwindow = (peak-0.025,peak+0.025)

    mean_amplitudes = {}
    mean_amplitudes["id"] = []
    mean_amplitudes["soa"] = []
    mean_amplitudes["num"] = [] 
    mean_amplitudes["run"] = [] 
    mean_amplitudes["type"] = [] 
    mean_amplitudes["amplitude_difference"] = [] 


    # Read file from disk
    raw_filename = utils.get_derivative_file_name(
        config[soa]["bids_root_path"], id, config[soa]["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    events_filename = utils.get_derivative_file_name(
        config[soa]["bids_root_path"], id, config[soa]["pipeline_name"], ".txt", suffix="eve", processing="prepared")
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

    epochs1 = epochs[cond1]
    epochs2 = epochs[cond2]

    idx1 = list(range(len(epochs1)))
    idx2 = list(range(len(epochs2)))

    for n in range(N):
        
        np.random.shuffle(idx1)
        np.random.shuffle(idx2)

        for num in nums:
            if num > len(idx1) or num > len(idx2):
                # mean_amplitudes["id"].append(id) 
                # mean_amplitudes["soa"].append(soa) 
                # mean_amplitudes["num"].append(num)
                # mean_amplitudes["run"].append(n)
                # mean_amplitudes["type"].append("full") 
                # mean_amplitudes["amplitude_difference"].append(np.nan)
                break

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
            mean_amplitudes["soa"].append(soa) 
            mean_amplitudes["num"].append(num)
            mean_amplitudes["run"].append(n)
            mean_amplitudes["type"].append("full") 
            mean_amplitudes["amplitude_difference"].append(np.mean(ma))

            ## split-half
            evokeds_h1 = {cond: [] for cond in [cond1, cond2]}
            evokeds_h2 = {cond: [] for cond in [cond1, cond2]}
            

            subsample_epochs1_h1 = epochs1[idx1[:num]][:int(num/2)]
            subsample_epochs1_h2 = epochs1[idx1[:num]][int(num/2):]

            subsample_epochs2_h1 = epochs2[idx2[:num]][:int(num/2)]
            subsample_epochs2_h2 = epochs2[idx2[:num]][int(num/2):]

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
            mean_amplitudes["soa"].append(soa) 
            mean_amplitudes["num"].append(num)
            mean_amplitudes["run"].append(n)
            mean_amplitudes["type"].append("half_1") 
            mean_amplitudes["amplitude_difference"].append(np.mean(ma_h1))

            mean_amplitudes["id"].append(id) 
            mean_amplitudes["soa"].append(soa) 
            mean_amplitudes["num"].append(num)
            mean_amplitudes["run"].append(n)
            mean_amplitudes["type"].append("half_2") 
            mean_amplitudes["amplitude_difference"].append(np.mean(ma_h2))

    return pd.DataFrame(mean_amplitudes)
   

def main():
    #parsl.load(pconfig)
    #parsl.set_stream_logger()

    ids1 = get_entity_vals(config["100"]["bids_root_path"], "sub")
    ids2 = get_entity_vals(config["150"]["bids_root_path"], "sub")

    tasks1 = [analyis_subsample(id, config, "100") for id in ids1]
    tasks2 = [analyis_subsample(id, config, "150") for id in ids2]

    mean_amplitudes = [i for i in tasks1 + tasks2]

    df = pd.concat(mean_amplitudes)
    df.to_csv("out2.csv")
    
    print(df)


if __name__ == '__main__':
    main()