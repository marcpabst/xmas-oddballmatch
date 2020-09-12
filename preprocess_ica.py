#%%
import mne
from autoreject import Ransac, AutoReject
from os import path
from functools import partial
import numpy as np
from reporting import Report

import matplotlib.gridspec as gridspec

import utils

import io
from contextlib import redirect_stdout

f = io.StringIO()

#rootpath = "/mnt/c/Users/Marc/Documents/Xmas_Oddballmatch/raw_biosemi"
rootpath = "/home/pabst/data/raw_biosemi"

# Reporting 
report = Report("Subject 01")

# Read data from Disk
raw = mne.io.read_raw_bdf(os.path.join(rootpath, "Xmas_01.bdf"), exclude = ["EXG8"], preload = True)
# Re-Reference
raw = raw.set_eeg_reference("average")
# Assign correct channel types 
raw = raw.set_channel_types({"SO2":"eog","IO2":"eog","LO1":"eog","LO2":"eog","Nose":"misc"})
# Rename channels to match MNE's montage
raw = raw.rename_channels({"FZ":"Fz", "PZ":"Pz", "OZ":"Oz", "CZ":"Cz", "FP2":"Fp2"})
# Load and apply standard 10-20 montage
ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
raw = raw.set_montage(ten_twenty_montage)
# Make copy of raw data
ica_raw = raw.copy()
# Report
fig1 = mne.viz.plot_raw_psd(ica_raw)
report.add_section(title = "Raw PSD", text = "Testest", plot = fig1)
# Filter data with 1-Hz-Highpass TODO: Specifiy filter
raw = raw.filter(l_freq = 2, fir_window = "hamming")

filt = mne.create_filter(ica_raw, l_freq=1., h_freq=None)
ica_raw = ica_raw.filter()
# Remove line noise using ZapLine
ica_raw = utils.apply_zapline(ica_raw, 50., picks = ["eeg","eog"], nremove = 3)
# Plot
fig2 = mne.viz.plot_raw_psd(ica_raw)
report.add_section(title = "PSD after Line Noise Removal (ZapLine)", text = "Testest", plot = fig1)
# Cut continous data into arbitrary epochs of 1 s
events = mne.make_fixed_length_events(ica_raw, duration=1.0)
epochs = mne.Epochs(ica_raw, events, tmin=0.0, tmax=1.0, reject=None, baseline=None, preload=True)
# Identify bad channels using RANSAC
ransac = Ransac(n_jobs=10, verbose='progressbar')
ransac.fit(epochs)
# Mark bad channels
ica_raw.info['bads'] +=  ransac.bad_chs_
n_bad_channels = len(ica_raw.info['bads'])
n_all_channels = len(mne.channel_indices_by_type(ica_raw.info)["eeg"])
# Interpolate bad channels
ica_raw = ica_raw.interpolate_bads(reset_bads=True)
# Using ASR
#ica_raw = utils.apply_asr(raw, (10, 20))
# Create ICA
ica = mne.preprocessing.ICA(n_components=n_all_channels-n_bad_channels, method="picard", fit_params=None, random_state=0)
# Fit ICA
ica.fit(ica_raw, picks="eeg")
# Plot components
ica.plot_components()
# Apply matrix to original data
raw = ica.apply(raw)
# Filter data
raw = raw.filter(l_freq = .1, h_freq = 30, fir_window = "hamming")
#%%
# Plot ICA components
figs3 = []
for index, component_name in enumerate(ica._ica_names):
    print(index, "\n")
    fig = plt.figure(figsize=(20,5))
    tfig = plt.figure(figsize=(25,4))
    gs = fig.add_gridspec(1, 3)
    axs = [ fig.add_subplot(gs[0]),
            tfig.add_subplot(111),
            tfig.add_subplot(111),
            fig.add_subplot(gs[1:2]),
            tfig.add_subplot(111) ]
    mne.viz.plot_ica_properties(ica, raw, index, axes = axs, show = False)
    figs3.append(fig)

report = Report2("Subject 01")
report.add_section(title = "ICA Components", plot = figs3)

report.write("test.pdf")


# %%
fig = plt.figure(figsize=(25,4))
gs = fig.add_gridspec(1, 5)
axs = [ fig.add_subplot(gs[0]),
    fig.add_subplot(gs[1]),
    fig.add_subplot(gs[2]),
    fig.add_subplot(gs[3]),
    fig.add_subplot(gs[4]) ]
mne.viz.plot_ica_properties(ica, raw, 3, axes = axs, show = False)

# %%
