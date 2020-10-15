#%%
import mne
import meegkit
import matplotlib.pyplot as plt
from meegkit.asr import ASR, clean_windows
from meegkit.utils.matrix import sliding_window
import numpy as np

#%%
raw = mne.io.read_raw_fif("/home/marc/sub-002_proc-prepared_raw.fif")
raw = raw.resample(128)
raw = raw.filter(
    l_freq=3, h_freq=35)
# %%
mne.io.write
raw.plot()
#%%
raw2 = raw.copy().pick("eeg")
raw3 = raw.copy().pick("eeg")

X = raw2.get_data()
sfreq = raw2.info["sfreq"]
nchan = X.shape[0]
asr = ASR(method='euclid', sfreq = sfreq)

data = np.double(X)

asr.fit(data)

X = np.double(sliding_window(data, window=int(sfreq), step=int(sfreq)))
Y = np.zeros_like(X)
for i in range(X.shape[1]):
    Y[:, i, :] = asr.transform(X[:, i, :])

clean = Y.reshape(nchan, -1)
#%%
raw3._data = clean
# %%
sample_mask = np.sum(np.abs(data * 1000000 - clean * 1000000), 0) < 1e-10
#%%

# find latency of regions
retain_data_intervals = np.reshape( np.argwhere(np.diff([False] + sample_mask + [False])), 2,[])
retain_data_intervals[:,1] = retain_data_intervals[:,1]-1
#%%
my_annot = mne.Annotations(onset=[3, 5, 7],
                           duration=[1, 0.5, 0.25],
                           description=['AAA', 'BBB', 'CCC'])