#%%
import mne
import matplotlib.pyplot as plt
from os import path
from functools import partial
import numpy as np
import pandas

rootpath = "/mnt/c/Users/Marc/Documents/Xmas_Oddballmatch/raw_biosemi"
eventsinfo = {
    "random/0/deviant": 102,
    "random/0/standard": 101,
    "random/1/standard": 111,
    "random/2/standard": 121,
    "random/3/standard": 131,
    "random/4/standard": 141,
    "random/5/deviant" : 152,
    "random/5/standard": 151,
    "random/nopattern/standard": 1,
    "random/nopattern/deviant": 2,
    "predictable/1/standard": 11,
    "predictable/2/standard": 21,
    "predictable/3/standard": 31,
    "predictable/4/standard": 41,
    "predictable/5/standard": 51,
    "predictable/5/deviant": 52
    }

# Plotting styles
plt.style.use(['science', 'retro', 'no-latex'])


def process_subject(
    filename, 
    id,
    l_freq = 1, 
    h_freq = 15,
    window = (-.1, .3),
    baseline = (-.1, 0),
    fir_window = "blackman",
    l_trans_bandwidth = "auto",
    h_trans_bandwidth = "auto"):
    """
    Docstring ...
    """
    
    # Read file from disk
    raw = mne.io.read_raw_bdf(os.path.join(rootpath, filename), preload = True)
    # Add ID to raw instance
    raw.info["id"] = id
    # Re-reference to nose channel
    raw = raw.set_eeg_reference(["Nose"])
    # Remap channel types for EOG
    raw = raw.set_channel_types({"SO2":"eog","IO2":"eog","LO1":"eog","LO2":"eog"})
    # Bipolarize EOG
    raw = mne.set_bipolar_reference(raw, "SO2", "IO2", "vEOG")
    raw = mne.set_bipolar_reference(raw, "LO1", "LO2", "hEOG")
    # Pick subset of channels to speed-up processing
    raw = raw.pick(["FZ", "vEOG", "hEOG", "Status"])

    # Extract events
    events = mne.find_events(raw, shortest_event=1)
    # Merge events
    events = mne.merge_events(events, [41, 98], 41)
    events = mne.merge_events(events, [52, 99], 52)

    # Filter data
    raw = raw.filter(l_freq = l_freq, h_freq = h_freq, fir_window = fir_window, l_trans_bandwidth = l_trans_bandwidth, h_trans_bandwidth = h_trans_bandwidth)

    # Create clusters to find peak latency
    #raw = mne.channels.combine_channels(raw, {"frontoCentralCluster" = [""]})
    

    # Epoch data
    epochs = mne.Epochs(raw, events, eventsinfo, 
        tmin=window[0], 
        tmax=window[1], 
        baseline = baseline,
        reject = {"eog": 100e-4})

    return epochs
#%%
processfunc = partial(process_subject, 
    baseline = (-.05, 0), 
    l_freq = 1,
    h_freq = 30,
    fir_window = "blackman",
    l_trans_bandwidth = .5,
    h_trans_bandwidth = 5.
    )
epochslist = [processfunc("Xmas_{:02d}.bdf".format(id), id) for id in range(1,20)]
#%% 
def get_evokeds(epochslist, conditions, grandaverage = False):
    try:
        out = [mne.combine_evoked([e[conditions[0]].average(), -e[conditions[1]].average()], "equal") for e in epochslist]
    except:
        out = [e[conditions].average() for e in epochslist]

    if grandaverage:
        return mne.grand_average(out)
    else:
        return out

def get_mean_amplitude(evoked, window = None):
    windowasindex = diff.time_as_index(peakwindow)
    return np.mean( diff.data[:, peakwindowasindex[0]:peakwindowasindex[1]] )
#%% Expecting a pronounced MMN here
fig1 = mne.viz.plot_compare_evokeds(
    {
        "Random Standard": get_evokeds(epochslist, "random/standard"),
        "Random Deviant": get_evokeds(epochslist, "random/deviant")
    },
    picks = "FZ",
    ci = True, 
    truncate_xaxis = False,
    truncate_yaxis = False
)

#%%(pred)BAAAA*B* vs. (pred)BAAA*A*
fig2 = mne.viz.plot_compare_evokeds(
    {
        "(pred)BAAAA*B*": get_evokeds(epochslist, "predictable/5/deviant"),
        "(pred)BAAA*A*": get_evokeds(epochslist, "predictable/4/standard")
    },
    picks = "FZ",
    truncate_xaxis = False,
    truncate_yaxis = False
)

#%% (rand)BAAAA*B* vs. (rand)BAAA*A*
fig3 = mne.viz.plot_compare_evokeds(
    {
        "(rand)BAAAA*B*": get_evokeds(epochslist, "random/5/deviant"),
        "(rand)BAAA*A*": get_evokeds(epochslist, "random/4/standard")
    },
    picks = "FZ",
    truncate_xaxis = False,
    truncate_yaxis = False
)

#%% (rand)BAAAA*A* vs. (rand)BAAA*A*
fig3 = mne.viz.plot_compare_evokeds(
    {
        "(rand)BAAAA*A*": get_evokeds(epochslist, "random/5/standard"),
        "(rand)BAAA*A*": get_evokeds(epochslist, "random/4/standard")
    },
    picks = "FZ",
    truncate_xaxis = False,
    truncate_yaxis = False
)

#%% (pred)BAAAA*A* vs. (pred)BAAA*A*
fig3 = mne.viz.plot_compare_evokeds(
    {
        "(rand)BAAAA*A*": get_evokeds(epochslist, "predictable/5/standard"),
        "(rand)BAAA*A*": get_evokeds(epochslist, "predictable/4/standard")
    },
    picks = "FZ",
    truncate_xaxis = False,
    truncate_yaxis = False
)
 
# %% H1
fig3 = mne.viz.plot_compare_evokeds(
    {
        "(rand)BAAAA*B* vs. (rand)BAAA*A*": get_evokeds(epochslist, ["random/5/deviant", "random/4/standard"]),
        "(pred)BAAAA*B* vs. (pred)BAAA*A*": get_evokeds(epochslist, ["predictable/5/deviant", "predictable/4/standard"])
    },
    picks = "FZ",
    truncate_xaxis = False,
    truncate_yaxis = False,
    legend = "upper center"
)
 
# %% Find peak and find a window (±25ms) 
diff = get_evokeds(epochslist, ["random/deviant", "random/standard"], grandaverage=True)
peak = diff.pick(picks="FZ").get_peak(tmin = .1, tmax = .2)[1]
peakwindow = (peak-0.025, peak+0.025)

meanamplitude = get_mean_amplitude(diff, windowpeakwindow)


# %%
conditions = {
    ("predictable", "standard"): "predictable/4/standard",
    ("predictable", "deviant"): "predictable/5/deviant",
    ("random", "standard"): "random/4/standard",
    ("random", "deviant"): "random/5/deviant"
}

avgfunc = partial(get_mean_amplitude, window = peakwindow)

rows = []
for condition in conditions:
    evoked = get_evokeds(epochslist, condition)
    rows.append({"Id": evoked.info["id"], "MeanAmplitude":evoked.avgfunc(evoked)})


# %%
