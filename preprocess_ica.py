#%%
import mne
from autoreject import Ransac, AutoReject
from os import path
from functools import partial
import numpy as np


rootpath = "/mnt/c/Users/Marc/Documents/Xmas_Oddballmatch/raw_biosemi"

# Read data from Disk
raw = mne.io.read_raw_bdf(os.path.join(rootpath, "Xmas_01.bdf"), exclude = ["EXG8"], preload = True)
# Assign correct channel types 
raw = raw.set_channel_types({"SO2":"eog","IO2":"eog","LO1":"eog","LO2":"eog","Nose":"misc"})
# Rename channels to match MNE's montage
raw = raw.rename_channels({"FZ":"Fz", "PZ":"Pz", "OZ":"Oz", "CZ":"Cz", "FP2":"Fp2"})
# Load and apply standard 10-20 montage
ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
raw = raw.set_montage(ten_twenty_montage)
# Cut continous data into arbitrary epochs of 1 s
events = mne.make_fixed_length_events(raw, duration=1.0)
epochs = mne.Epochs(raw, events, tmin=0.0, tmax=1.0, reject=None, baseline=None, preload=True)
#%%
# Identify bad channels using RANSAC
ransac = Ransac(n_jobs=2, verbose='progressbar')
ransac.fit_transform(epochs)
#%%
# Mark bad channels
raw.info['bads'] +=  ransac.bad_chs_
# Interpolate bad channels
raw = raw.interpolate_bads(reset_bads=True)
#%%
# Identify bad epochs
autoreject = AutoReject(random_state=42, n_jobs=2)
epochs_clean, epochs_reject = autoreject.fit_transform(epochs, return_log=True)
#%%
# Re-concatenate epochs
longepoch = mne.concatenate_epochs(epochs_clean)
# Create ICA object
ica = mne.preprocessing.ICA(n_components=20, method="fastica", fit_params=None, random_state=0)
# Fit ICA
ica.fit(longepoch, picks="eeg")
# Plot components
ica.plot_components()
# Apply matrix to original data

