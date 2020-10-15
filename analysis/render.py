import mne

import matplotlib
ica = mne.preprocessing.ica.read_ica_eeglab("../matlab.set")
raw = mne.io.read_raw_eeglab("../matlab.set")
ica.info = raw.info
ica._update_ica_names()
matplotlib.use("Qt5Agg")

def upper(p):
    return p.upper()


besa = mne.channels.read_custom_montage("../standard-10-5-cap385.elp")
ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')

ica.info.set_montage(besa, match_case=False, on_missing="raise")
ica.info.set_montage(ten_twenty_montage, match_case=True, on_missing="ignore")

ica.plot_components(cmap="rainbow", picks=[0, 1, 2 ,3, 4], outlines = "head", colorbar=True,topomap_args = {"extrapolate": "head", "border":0,  contours=5, sensors="k+")

