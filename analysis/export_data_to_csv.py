
# %%
bids_root_path_100 = "/media/marc/Medien/xmasoddballmatch-bids"
pipeline_name_100 = "pipeline01"        
    
bids_root_path_150 = "/media/marc/Medien/machristine-bids"
pipeline_name_150 = "pipeline_christine"


# %%
from preprocessing.configuration import load_configuration

import utils

from os.path import join
import mne
from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

import plotting

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import ptitprince as pt
import pandas as pd
import matplotlib.gridspec as gridspec
import scipy as sp
from copy import deepcopy

config = load_configuration("../configuration/pipeline01_100.yml")

plt.ioff()


# %%
def difference_wave(evokeds_as_dict, conditions, grandaverage=False):
    out = [mne.combine_evoked([a, b], [1,-1]) for a, b in zip(
        evokeds_as_dict[conditions[0]], evokeds_as_dict[conditions[1]])]
    if grandaverage:
        return mne.grand_average(out)
    else:
        return out

#%%
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

def get_amplitudes(evokeds, i, picks = "all"):

    means = []
    if isinstance(evokeds, list):
        for i, evoked in enumerate(evokeds):
            evoked = evoked.copy().pick(picks)

            data = evoked.data[:, i]
            mean = data.mean()
            means.append(mean)
    else:
        return get_mean_amplitudes([evokeds], i, picks)[0]

    return means

# %% [markdown]
# ## Load Data From Disk

# %%
ids_100 = get_entity_vals(join(bids_root_path_100, "derivatives"), "sub") 
ave_filenames_100 = [utils.get_derivative_file_name(
        bids_root_path_100, id, pipeline_name_100, ".fif", suffix="ave") for id in ids_100]
all_evokeds_100 = [mne.read_evokeds(ave_filename) for ave_filename in ave_filenames_100]

ids_150 = get_entity_vals(join(bids_root_path_150, "derivatives"), "sub") 
ave_filenames_150 = [utils.get_derivative_file_name(
        bids_root_path_150, id, pipeline_name_150, ".fif", suffix="ave") for id in ids_150]
all_evokeds_150 = [mne.read_evokeds(ave_filename) for ave_filename in ave_filenames_150]

evokeds_list_as_dict = {}

evokeds_list_as_dict["100"] = {key: [] for key in config["conditions_of_interest"]}

for evokeds_list in all_evokeds_100:
    for evoked in evokeds_list:
        try:
            evokeds_list_as_dict["100"][evoked.comment].append(evoked)
        except KeyError:
            pass
            print("Missing condition in list.")

evokeds_list_as_dict["150"] = {key: [] for key in config["conditions_of_interest"]}

for evokeds_list in all_evokeds_150:
    for evoked in evokeds_list:
        try:
            evokeds_list_as_dict["150"][evoked.comment].append(evoked)
        except KeyError:
            pass
            print("Missing condition in list.")

# %%
# Find peak and find a window (±25ms) 
diff = difference_wave(evokeds_list_as_dict["100"], ("random/5/deviant", "random/4/standard"), grandaverage=True)
peak_latency = diff.pick(picks=["F3", "FZ", "F4", "FC1", "FC2"]).get_peak(tmin = .1, tmax = .170,  return_amplitude = True)[1]

peakwindow_100 = (peak_latency-0.025, peak_latency+0.025)

print("100 ms: Peak Latency is {} s.".format(peakwindow_100))


diff = difference_wave(evokeds_list_as_dict["150"], ("random/5/deviant", "random/4/standard"), grandaverage=True)
peak_latency = diff.pick(picks=["F3", "FZ", "F4", "FC1", "FC2"]).get_peak(tmin = .1, tmax = .170,  return_amplitude = True)[1]

peakwindow_150 = (peak_latency-0.025, peak_latency+0.025)

print("150 ms: Peak Latency is {} s.".format(peakwindow_150))

# %% [markdown]
# ## Create DataFrame containing Mean Amplitudes

# %%
conditions       = {("100", "random", "B"): "random/5/deviant",
                    ("100", "random", "A"): "random/4/standard",
                    ("100", "predictable", "B"): "predictable/5/deviant",
                    ("100", "predictable", "A"): "predictable/4/standard",

                    ("150", "random", "B"): "random/5/deviant",
                    ("150", "random", "A"): "random/4/standard",
                    ("150", "predictable", "B"): "predictable/5/deviant",
                    ("150", "predictable", "A"): "predictable/4/standard"}

electrodes = {"FZ":"FZ", "CZ":"CZ", "M1": "M1", "M2": "M2", "fronto_pooled": ["FZ", "F3", "F4", "FC1", "FC2"], "mastoids_pooled": ["M1", "M2"]}

amplitudes = [{ "SOA":key[0], "Participant":key[0] + "_" + str(i), 
                "Condition":key[1], "StimulusType":key[2], 
                "MeanAmplitude": amplitude,
                "Electrode": electrode} 
                    for key,value in conditions.items() 
                    for electrode, pick in electrodes.items()
                    for i, amplitude in enumerate(get_mean_amplitudes(evokeds_list_as_dict[key[0]][value], peakwindow_100, picks=pick)) ]
amplitudes_df = pd.DataFrame(amplitudes)

amplitudes_df.to_csv("../data/mean_amplitudes.csv", index=False)

amplitudes_df

# %%
# %%
conditions       = {("100", "random", "B"): "random/5/standard",
                    ("100", "random", "A"): "random/4/standard",
                    ("100", "predictable", "B"): "predictable/5/standard",
                    ("100", "predictable", "A"): "predictable/4/standard",

                    ("150", "random", "B"): "random/5/standard",
                    ("150", "random", "A"): "random/4/standard",
                    ("150", "predictable", "B"): "predictable/5/standard",
                    ("150", "predictable", "A"): "predictable/4/standard"}

electrodes = {"FZ":"FZ", "CZ":"CZ", "M1": "M1", "M2": "M2", "fronto_pooled": ["FZ", "F3", "F4", "FC1", "FC2"], "mastoids_pooled": ["M1", "M2"]}

amplitudes = [{ "SOA":key[0], "Participant":key[0] + "_" + str(i), 
                "Condition":key[1], "StimulusType":key[2], 
                "MeanAmplitude": amplitude,
                "Electrode": electrode} 
                    for key,value in conditions.items() 
                    for electrode, pick in electrodes.items()
                    for i, amplitude in enumerate(get_mean_amplitudes(evokeds_list_as_dict[key[0]][value], peakwindow_100, picks=pick)) ]
amplitudes_df = pd.DataFrame(amplitudes)

amplitudes_df.to_csv("../data/mean_amplitudes2.csv", index=False)



#%%
def get_sequence(data, soa, c, picks = "FZ"):
    evo1 = mne.grand_average(data[c+"/1/standard"]).copy()
    evo1.crop(-.025,soa).pick(picks)

    evo2 = mne.grand_average(data[c+"/2/standard"]).copy()
    evo2.crop(0,soa).pick(picks)

    evo3 = mne.grand_average(data[c+"/3/standard"]).copy()
    evo3.crop(0,soa).pick(picks)

    evo4 = mne.grand_average(data[c+"/4/standard"]).copy()
    evo4.crop(0,1.5*soa).pick(picks)

    return zip(*(np.hstack([np.squeeze(evo1.times),
                            np.squeeze(evo2.times) + 1 * soa,
                            np.squeeze(evo3.times) + 2 * soa,
                            np.squeeze(evo4.times) + 3 * soa]).tolist(),     

            np.hstack([np.squeeze(evo1.data * 10e5),
                            np.squeeze(evo2.data * 10e5),
                            np.squeeze(evo3.data * 10e5),
                            np.squeeze(evo4.data * 10e5)]).tolist() ))

electrodes = {"FZ":"FZ", "CZ":"CZ", "M1": "M1", "M2": "M2", "fronto_pooled": ["FZ", "F3", "F4", "FC1", "FC2"], "mastoids_pooled": ["M1", "M2"]}

conditions =       [("100", 0.100, "random"),
                    ("100", 0.100, "predictable"),
                    ("150", 0.150, "random"),
                    ("150", 0.150, "predictable")]

sequences  = [{ "SOA":key[0],
                "Condition":key[2], 
                "Time": time,
                "Voltage": v,
                "Electrode": electrode} 
                    for key in conditions 
                    for electrode, pick in electrodes.items()
                    for time, v in get_sequence(evokeds_list_as_dict[key[0]], key[1], key[2], picks=pick)
                    ]

sequences_df = pd.DataFrame(sequences)

sequences_df.to_csv("../data/sequences.csv", index=False)

# %%
conditions       = {("100", "random", "B"): "random/deviant",
                    ("100", "random", "A"): "random/4/standard",

                    ("150", "random", "B"): "random/deviant",
                    ("150", "random", "A"): "random/4/standard"}

electrodes = {"FZ":"FZ", "CZ":"CZ", "M1": "M1", "M2": "M2", "fronto_pooled": ["FZ", "F3", "F4", "FC1", "FC2"], "mastoids_pooled": ["M1", "M2"]}

amplitudes = [{ "SOA":key[0], "Participant":key[0] + "_" + str(i), 
                "Condition":key[1], "StimulusType":key[2], 
                "MeanAmplitude": amplitude,
                "Electrode": electrode} 
                    for key,value in conditions.items() 
                    for electrode, pick in electrodes.items()
                    for i, amplitude in enumerate(get_mean_amplitudes(evokeds_list_as_dict[key[0]][value], peakwindow_100, picks=pick)) ]
amplitudes_df = pd.DataFrame(amplitudes)

amplitudes_df.to_csv("../data/mean_amplitudes_random_alt.csv", index=False)

amplitudes_df



# %%
