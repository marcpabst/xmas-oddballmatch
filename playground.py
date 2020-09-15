#%%
import mne
import matplotlib.pyplot as plt

import plotting
#%%

#rootpath = "/mnt/c/Users/Marc/Documents/Xmas_Oddballmatch/raw_biosemi"
rootpath = "/home/pabst/data/raw_biosemi"

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
    "predictable/5/deviant": 52,

    "begin": 65790,
    "end": 65536
    }

# Plotting styles
#plt.style.use(['science', 'retro', 'no-latex'])


def process_subject(
    filename, 
    id,
    l_freq = .1, 
    h_freq = 30,
    window = (-.1, .3),
    baseline = (-.1, 0),
    fir_window = "hamming",
    l_trans_bandwidth = "auto",
    h_trans_bandwidth = "auto",
    report_dir = "reports"):
    """
    Docstring ...
    """
    #### Prepare Reporting ####
    report = Report("Participant No. {id}".format(id=id))

    #### Prepare Data ####
    # Read file from disk
    raw = mne.io.read_raw_bdf(os.path.join(rootpath, filename), exclude = ["EXG8"], preload = True)
    # Add ID to raw instance
    raw.info["id"] = id
    # Rename channels to match MNE's montage
    raw = raw.rename_channels({"FZ":"Fz", "PZ":"Pz", "OZ":"Oz", "CZ":"Cz", "FP2":"Fp2"})
    # Re-Reference
    raw = raw.set_eeg_reference("average")
    # Assign correct channel types 
    raw = raw.set_channel_types({"SO2":"eog","IO2":"eog","LO1":"eog","LO2":"eog","Nose":"misc"})
    # Load and apply standard 10-20 montage
    ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
    raw = raw.set_montage(ten_twenty_montage)
    # Read events
    events = mne.find_events(raw, shortest_event=1)
    # Report raw power
    fig = mne.viz.plot_raw_psd(raw)
    report.add_section(title = "PSD for raw data", plot = fig)
    
    #### ICA ####
    # Make copy of raw data
    ica_raw = raw.copy()
    # Cut non-block data
    ica_raw = utils.cut_raw_blocks(ica_raw, events, eventsinfo, "begin", "end")
    # Remove line noise using ZapLine
    ica_raw = utils.apply_zapline(ica_raw, 50., picks = ["eeg"], nremove = 8)
    # Filter 
    ica_raw = ica_raw.filter(l_freq=1., h_freq=None, fir_window = "blackman")
    # Plot
    fig = mne.viz.plot_raw_psd(ica_raw)
    report.add_section(title = "PSD after Line Noise Removal (ZapLine) and Filtering", plot = fig)
    # Cut continous data into arbitrary epochs of 1 s
    events = mne.make_fixed_length_events(ica_raw, duration=1.0)
    epochs = mne.Epochs(ica_raw, events, tmin=0.0, tmax=1.0, reject=None, baseline=None, preload=True)
    # Identify bad channels using RANSAC
    ransac = Ransac(n_jobs=10, verbose='progressbar')
    ransac.fit(epochs)
    ica_raw.info['bads'] +=  ransac.bad_chs_
    n_bad_channels = len(ica_raw.info['bads'])
    n_all_channels = len(mne.channel_indices_by_type(ica_raw.info)["eeg"])
    # Interpolate bad channels
    ica_raw = ica_raw.interpolate_bads(reset_bads=True)
    # Create ICA
    n_pca_components = n_all_channels-n_bad_channels-1
    ica = mne.preprocessing.ICA(n_components=n_pca_components, method="picard", fit_params=None, random_state=42)
    # Fit ICA
    ica.fit(ica_raw, picks=["eeg"])
    # Plot components
    figs = []
    for index, component_name in enumerate(ica._ica_names):
        fig = plt.figure(figsize=(20,5))
        tfig = plt.figure(figsize=(25,4))
        gs = fig.add_gridspec(1, 3)
        axs = [ fig.add_subplot(gs[0]),
                tfig.add_subplot(111),
                tfig.add_subplot(111),
                fig.add_subplot(gs[1:2]),
                tfig.add_subplot(111) ]
        mne.viz.plot_ica_properties(ica, raw, index, axes = axs, show = False)
        figs.append(fig)

    report.add_section(title = "ICA Components", plot = figs)
    # Apply matrix to original data
    raw = ica.apply(raw)


    #### Segment ####
    # Bipolarize EOG
    raw = mne.set_bipolar_reference(raw, "SO2", "IO2", "vEOG")
    raw = mne.set_bipolar_reference(raw, "LO1", "LO2", "hEOG")
    # Re-reference
    raw = raw.set_eeg_reference(["Nose"])
    # Extract events
    events = mne.find_events(raw, shortest_event=1)
    # Merge events
    events = mne.merge_events(events, [41, 98], 41)
    events = mne.merge_events(events, [52, 99], 52)

    # Filter data
    raw = raw.filter(l_freq = l_freq, h_freq = h_freq, fir_window = fir_window, l_trans_bandwidth = l_trans_bandwidth, h_trans_bandwidth = h_trans_bandwidth)

    # Epoch data
    epochs = mne.Epochs(raw, events, eventsinfo, 
        tmin=window[0], 
        tmax=window[1], 
        baseline = baseline,
        reject = {"eog": 100e-4})

    report.write(os.path.join(report_dir, str(id)+"-test.pdf"))
    return epochs
#%%
from joblib import Parallel, delayed
processfunc = partial(process_subject, 
    baseline = (-.05, 0), 
    #l_freq = 1,
    #h_freq = 30,
    #fir_window = "blackman",
    #l_trans_bandwidth = .5,
    #h_trans_bandwidth = 5.
    )
#epochslist = Parallel(n_jobs=-3)(delayed(processfunc)("Xmas_{:02d}.bdf".format(id), id) for id in range(1,2))
epochslist = [processfunc("Xmas_{:02d}.bdf".format(id), id) for id in range(1,2)]


#%% 
def get_evokeds(epochslist, conditions, grandaverage = False):
    if type(conditions) is list or type(conditions) is tuple:
        out = [mne.combine_evoked([e[conditions[0]].average(), -e[conditions[1]].average()], "equal") for e in epochslist]
    else:
        out = [e[conditions].average() for e in epochslist]

    if grandaverage:
        return mne.grand_average(out)
    else:
        return out

def get_mean_amplitude(evoked, window = None):
    windowasindex = evoked.time_as_index(window)
    return np.mean( evoked.data[:, windowasindex[0]:windowasindex[1]] )
#%% Expecting a pronounced MMN here
dat1 = {
        "Random Standard": get_evokeds(epochslist, "random/standard"),
        "Random Deviant": get_evokeds(epochslist, "random/deviant")
     }
#%%
fig1 = mne.viz.plot_compare_evokeds(
    dat1,
    picks = "M2",
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
    picks = "",
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
peak = diff.pick(picks="Fz").get_peak(tmin = .1, tmax = .2)[1]
peakwindow = (peak-0.025, peak+0.025)

meanamplitude = get_mean_amplitude(diff, window=peakwindow)


# %%
conditions = {
    ("predictable", "standard"): "predictable/4/standard",
    ("predictable", "deviant"): "predictable/5/deviant",
    ("random", "standard"): "random/4/standard",
    ("random", "deviant"): "random/5/deviant"
}

avgfunc = partial(get_mean_amplitude, window = peakwindow)

rows = []
for key, condition in conditions.items():
    print(condition)
    evokeds = get_evokeds(epochslist, condition)
    [rows.append({"Id": evoked.info["id"], "Predictability":key[0], "Deviance":key[1], "MeanAmplitude":avgfunc(evoked)}) for evoked in evokeds]

#%%
data = pandas.DataFrame(rows)
anova = statsmodels.stats.anova.AnovaRM(data,"MeanAmplitude","Id", within = ["Predictability", "Deviance"])
results = anova.fit()




# %%
raw = mne.io.read_raw_fif("/home/pabst/data/xmasoddballmatch-bids/derivatives/pipeline01/sub-001/sub-001_proc-prepared_raw.fif")
ica = mne.preprocessing.read_ica("/home/pabst/data/xmasoddballmatch-bids/derivatives/pipeline01/sub-001/sub-001_ica.fif")
# %%
import pandas as pd

csv_filename = "/home/pabst/data/xmasoddballmatch-bids/derivatives/pipeline01/sub-001/sub-001_ica-matlab.csv"
labels = pd.read_csv(csv_filename)

labels_names = labels.columns.tolist()
labels_confidence = labels.iloc[1].tolist()
plotting.plot_ica_component_simple(ica, raw, 1, labels_names, labels_confidence)
# %%
import mne

raw_filename = "/home/pabst/data/xmasoddballmatch-bids/derivatives/pipeline01/sub-001/sub-001_proc-prepared_raw.fif"
events_filename = "/home/pabst/data/xmasoddballmatch-bids/derivatives/pipeline01/sub-001/sub-001_proc-prepared_eve.txt"
raw = mne.io.read_raw_fif(raw_filename, preload=True)
events = mne.read_events(events_filename)

    
ica_filename = "/home/pabst/data/xmasoddballmatch-bids/derivatives/pipeline01/sub-001/sub-001_ica.fif"
ica = mne.preprocessing.read_ica(ica_filename)
#%%

# Epoch data
epochs = mne.Epochs(raw, events, config["events_dict"],
                    tmin=config["epoch_window"][0],
                    tmax=config["epoch_window"][1],
                    baseline=config["baseline_winow"],
                    reject={"eog": 100e-4}, preload=True).pick(picks="eeg")
            


# %%
import mne
from mne_bids.utils import get_entity_vals
from configuration import load_configuration
from os.path import join
import utils
config = load_configuration()
# Get subjects ids
ids = get_entity_vals(join(config["bids_root_path"], "derivatives"), "sub")

# Read files from disk
ave_filenames = [utils.get_derivative_file_name(
    config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave") for id in ids]
all_evokeds = [mne.read_evokeds(ave_filename) for ave_filename in ave_filenames]
#%%
# Report evoked
evokeds_list_as_dict = {}
evokeds_list_as_dict["random/deviant"] = []
evokeds_list_as_dict["random/standard"] = []
for evokeds_list in all_evokeds:
    for evoked in evokeds_list:
        evokeds_list_as_dict[evoked.comment].append(evoked)



figure = mne.viz.plot_compare_evokeds(evokeds_list_as_dict, picks=["F3", "Fz", "F4", "FC1", "FC2"], combine = "mean")
# %%
