from configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time
import pandas as pd
import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = load_configuration("../configuration/pipeline01_100.yml")
config["100"] = {}
config["100"]["bids_root_path"] = "/nfs/user/mo808sujo/xmasoddballmatch-bids"
config["100"]["pipeline_name"] = "pipeline01"

config["150"] = {}
config["150"]["bids_root_path"] = "/nfs/user/mo808sujo/machristine-bids"
config["150"]["pipeline_name"] = "pipeline_christine"

#config["100"]["bids_root_path"] = "/media/marc/Medien/xmasoddballmatch-bids"
#config["150"]["bids_root_path"] = "/media/marc/Medien/machristine-bids"

    

def analyis_subsample(id, config, soa):
    import mne
    import sys
    import numpy as np
    import pandas as pd
    from mne_bids import make_bids_basename, read_raw_bids, write_raw_bids
    from os.path import join, exists
    

    def split_in_half(epochs):
        if (len(epochs) % 2) != 0: raise ValueError(str(len(epochs)) + " is not even.")

        n = int(len(epochs) / 2)

        idx = list(range(len(epochs)))
        np.random.shuffle(idx)
        
        return epochs[idx[:n]], epochs[idx[n:]]

    def get_mean_amplitudes(evoked, window, picks = "all"):

        evoked = evoked.copy().pick(picks)

        _window = np.arange(evoked.time_as_index(window[0]),
                            evoked.time_as_index(window[1]))

        data = evoked.data[:, _window]
        mean = data.mean()
    
        return mean

    def get_derivative_file_name(bids_root_path, subject, pipeline_name, extension="", make_dir = True, **kwargs):

        derivivite_root_path = join(bids_root_path, "derivatives", pipeline_name) 
        save_dir = join(derivivite_root_path, "sub-"+subject)
        bids_basename = make_bids_basename(subject=subject, **kwargs)

        if make_dir and not exists(save_dir):
            makedirs(save_dir)

        return join(save_dir, bids_basename) + extension


    #nums = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, ]
    nums = list(range(100, 3000, 100))
    N = 200
    cond1 = "random/standard"
    cond2 = "random/deviant"
    peak = 0.132
    peakwindow = (peak-0.025,peak+0.025)

    mean_amplitudes = {}
    mean_amplitudes["id"] = []
    mean_amplitudes["soa"] = []
    mean_amplitudes["num"] = [] 
    mean_amplitudes["run"] = [] 
    mean_amplitudes["type"] = [] 
    mean_amplitudes["amplitude_difference"] = [] 


    # Read file from disk
    raw_filename = get_derivative_file_name(
        config[soa]["bids_root_path"], id, config[soa]["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    events_filename = get_derivative_file_name(
        config[soa]["bids_root_path"], id, config[soa]["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

    # Epoch data
   
    epochs = mne.Epochs(raw, events, config["events_dict"],
                        tmin=config["epoch_window"][0],
                        tmax=config["epoch_window"][1],
                        baseline=None,
                        reject=config["diff_criterion"],
                        preload=True)
    raw.pick(["FZ"])
    # raw = raw.set_channel_types(
    #     {"vEOG": "eog", "hEOG": "eog"})

    epochs1 = epochs[cond1]
    epochs2 = epochs[cond2]


    for n in range(N):
        print("Run " + str(n) + "...")

        idx1 = list(range(len(epochs1)))
        idx2 = list(range(len(epochs2)))
        
        np.random.shuffle(idx1)
        np.random.shuffle(idx2)


        for num in nums:
            print("Subsetting " + str(num) + " epochs.")
            print(len(idx1))
            print(len(idx2))

            if num > len(idx1) or num > len(idx2):
                print("Too few epochs.")
                break

    
            ## split-half ##
            t1 = split_in_half(epochs2[idx2[:num]])
            #t2 = split_in_half(epochs2[idx2[:num]])
            
            halves_avg = (t1[0].average(), t1[1].average())
 

            ma_h1 = get_mean_amplitudes(halves_avg[0], peakwindow, picks = ["FZ"]) 
            ma_h2 = get_mean_amplitudes(halves_avg[1], peakwindow, picks = ["FZ"]) 

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


            print("DIAGNOSTICS")
            print(ma_h1, ma_h2)

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
    df.to_csv("out.csv")
    
    print(df)


if __name__ == '__main__':
    main()