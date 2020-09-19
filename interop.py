from oct2py import Struct, Oct2Py
from collections import OrderedDict
import mne
import numpy as np
from functools import partial

from mne.io.eeglab.eeglab import _get_info
from mne.fixes import _safe_svd


class EEGlab():
    """
    Wrapper object for EEGLAB.
    """
    session = None

    def __init__(self):
        self.session = Oct2Py()
        self.session.addpath(
            "/share/projects/pabst/xmasoddballmatch/xmas-oddballmatch/matlab/eeglab")
        self.session.addpath(self.session.genpath(
            "/share/projects/pabst/xmasoddballmatch/xmas-oddballmatch/matlab/eeglab/functions/"))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.exit()

    def __getattr__(self, name):
        def wrapper(*args):
            for arg in args:
                print("ARG: ", type(arg))
            
            r = getattr(self.session, str(name))(*args)
            
            if hasattr(args[0], "inst"): # check whether first argument is an EEG object
                info = args[0].inst.info
                eeg = args[0]

                eeg.update_raw_from_eeglab(r)
                
                try:
                    eeg.update_ica_from_eeglab(r)
                except:
                    print("No ICA solution found. Skipping conversion.")

                return eeg
            
            return r

        return wrapper


class EEG(object):
    """
    Wraps an MNE's Raw instance and optionally instances of ICA, etc.
    """

    inst = None
    ica = None

    def __init__(self, inst=None, ica=None):
        self.inst = inst

    def __setitem__(self, floor_number, data):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

    def __getitem__(self, name):
        if name == "data" and isinstance(self.inst, mne.io.Raw):
            return self.inst.get_data() * 1000000
        elif name == "data" and isinstance(inst, mne.io.Epochs):
            return np.transpose(self.inst.get_data(), [1, 2, 0]) * 1000000
        elif name == "srate":
            return self.inst.info["sfreq"]
        elif name == "nbchan":
            return self.inst.info["nchan"]
        elif name == "times":
            return self.inst.times / 1000
        elif name == "trials":
            return 1
        elif name == "xmin":
            return 0
        elif name == "xmax":
            return 1
        elif name == "ref":
            return "average"
        elif name == "pnts":
            return len(self.inst.times)
        elif name == "setname":
            return "n/a"
        elif name == "event":
            return []
        elif name == "icaact":
            return []
        elif name == "chanlocs":
            r = Struct()
            r["labels"] = [ch["ch_name"] for ch in self.inst.info["chs"]]
            return r
        elif name == "icasphere":
            return []
        elif name == "icaweights":
            return []
        elif name == "icawinv":
            return []
        else:
            return None

    def get_instance(self):
        return self.inst

    def get_ica(self):
        return self.ica

    def items(self):
        return OrderedDict([
            ["data", self["data"]],
            ["srate", self["srate"]],
            ["nbchan", self["nbchan"]],
            ["xmin", self["xmin"]],
            ["xmax", self["xmax"]],
            ["ref", self["ref"]],
            ["pnts", self["pnts"]],
            ["setname", self["setname"]],
            ["event", self["event"]],
            ["icaact", self["icaact"]],
            ["icaweights", self["icaweights"]],
            ["icasphere", self["icasphere"]],
            ["icawinv", self["icawinv"]],
            ["chanlocs", self["chanlocs"]]]).items()

    @property
    def __class__(self):
        return dict
    
    def update_ica_from_eeglab(self, eeg):

        # TODO: Maybe taking the info dict from inst?
        info = _get_info(eeg)[0]
        mne.pick.pick_info(info, np.round(eeg['icachansind']).astype(int) - 1, copy=False)

        n_components = eeg.icaweights.shape[0]

        ica = mne.preprocessing.ICA(method='imported_eeglab', n_components=n_components)

        ica.current_fit = "eeglab"
        ica.ch_names = info["ch_names"]
        ica.n_pca_components = None
        ica.max_pca_components = n_components
        ica.n_components_ = n_components

        ica.pre_whitener_ = np.ones((len(eeg.icachansind), 1))
        ica.pca_mean_ = np.zeros(len(eeg.icachansind))

        n_ch = len(ica.ch_names)
        assert eeg.icaweights.shape == (n_components, n_ch)
        if n_components < n_ch:
            # When PCA reduction is used in EEGLAB, runica returns
            # weights= weights*sphere*eigenvectors(:,1:ncomps)';
            # sphere = eye(urchans), so let's use SVD to get our square
            # weights matrix (u * s) and our PCA vectors (v) back
            u, s, v = _safe_svd(eeg.icaweights, full_matrices=False)
            ica.unmixing_matrix_ = u * s
            ica.pca_components_ = v
        else:
            ica.unmixing_matrix_ = eeg.icaweights
            ica.pca_components_ = eeg.icasphere
        ica._update_mixing_matrix()
        
        self.ica = ica

    def update_raw_from_eeglab(self, eeg):
        info = self.inst.info.copy()
        data = eeg.data.T
        self.inst = mne.io.RawArray(data, info)
        
def eeg_from_matlab(eeg_struct):
    eeg = EEG()
    eeg.set_raw_from_eeglab(eeg_struct)
    return eeg
    
