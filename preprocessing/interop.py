from pymatbridge import Matlab
from collections import OrderedDict
import mne
import numpy as np
from functools import partial

from mne.io.eeglab.eeglab import _get_info
from mne.fixes import _safe_svd
from numpy.core.records import fromarrays

from os.path import join

from scipy.io import savemat
import scipy.io as spio

import warnings

tmp_path = "/share/tmpdata/pabst/"


class EEGlab():
    """
    Wrapper object for EEGLAB.
    """
    session = None    

    def __init__(self):
        self.session = Matlab()  
        self.session.start()
        self.session.run_func("addpath",
            "/share/projects/pabst/xmasoddballmatch/xmas-oddballmatch/matlab/eeglab")
        self.session.eval("addpath(genpath('/share/projects/pabst/xmasoddballmatch/xmas-oddballmatch/matlab/eeglab/functions/'))")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.run_func("exit")

    def __getattr__(self, name):
        def wrapper(*args):
            for arg in args:
                print("ARG: ", type(arg))


            if hasattr(args[0], "inst"):
                new_args = list(args)
                new_args[0] = args[0].to_dict()
            else:
                new_args = args

            
            #r = getattr(self.session, str(name))()
            #r = self.session.run_func(name, *args)
            # save to temp file
            fpath = join(tmp_path, "tmp.mat")
            savemat(fpath, {"ARGS": new_args})
            run = self.session.run_code("load('{}')".format(fpath))
            print(run["content"]["stdout"])
            run = self.session.run_code("RES = {}(ARGS{{:}})".format(name))
            print(run["content"]["stdout"])
            run = self.session.run_code("save('{}', 'RES')".format(fpath))
            print(run["content"]["stdout"])

            r = loadmat(fpath)["RES"]

            return r
            
            if hasattr(args[0], "inst"): # check whether first argument is an EEG object
                info = args[0].inst.info
                eeg = args[0]

                #eeg.update_raw_from_eeglab(r)
                
                #try:
                #    eeg.update_ica_from_eeglab(r)
                #except:
                #    print("No ICA solution found. Skipping conversion.")
                return eeg
            else:
                return r

        return wrapper


class EEG(object):
    """
    Wraps an MNE's Raw instance and optionally instances of ICA, etc.
    """

    inst = None
    ica = None

    def __init__(self, inst=None, ica=None):
        if "stim" in inst:
            warnings.warn("Your instance does contain at least one `stim`  channel that miht not be compatibly with EEGLAB. Consider dropping this channel.", RuntimeWarning)

        self.inst = inst

    def __setitem__(self, floor_number, data):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

    def __getitem__(self, name):
        if name == "data" and isinstance(self.inst, mne.io.Raw):
            data = self.inst.get_data()
            return np.double(data * 1000000)
        elif name == "data" and isinstance(self.inst, mne.epochs.Epochs):
            return np.double(np.transpose(self.inst.get_data(), [1, 2, 0]) * 1000000)
        elif name == "srate":
            return np.double(self.inst.info["sfreq"])
        elif name == "nbchan":
            return np.double(self.inst.info["nchan"])
        elif name == "times":
            return np.double(self.inst.times / 1000)
        elif name == "trials" and isinstance(self.inst, mne.io.Raw):
            return np.double(1)
        elif name == "trials" and isinstance(self.inst, mne.epochs.Epochs):
            return np.double(len(self.inst))
        elif name == "xmin":
            return np.double(self.inst.times[0])
        elif name == "xmax":
            return np.double(self.inst.times[-1])
        elif name == "ref":
            return "average"
        elif name == "pnts":
            return np.double(len(self.inst.times))
        elif name == "setname":
            return "n/a"
        elif name == "event":
            return []
        elif name == "icaact":
            return []
        elif name == "chanlocs":
            labs = [ch["ch_name"] for ch in self.inst.info["chs"]]
            r = fromarrays([labs], names=['labels'])
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
    def to_dict(self):
        return OrderedDict([
            ["data", self["data"]],
            ["srate", self["srate"]],
            ["nbchan", self["nbchan"]],
            ["xmin", self["xmin"]],
            ["xmax", self["xmax"]],
            ["ref", self["ref"]],
            ["pnts", self["pnts"]],
            ["setname", self["setname"]],
            ["trials", self["trials"]],
            ["event", self["event"]],
            ["icaact", self["icaact"]],
            ["icaweights", self["icaweights"]],
            ["icasphere", self["icasphere"]],
            ["icawinv", self["icawinv"]],
            ["chanlocs", self["chanlocs"]]])

    def items(self):
        self.to_dict().items()

    @property
    def __class__(self):
        return dict
    
    def update_ica_from_eeglab(self, eeg):
        # eeg = eeg.copy()
        eeg.chanlocs = [{f: getattr(chl, f) for f in chl._fieldnames} for chl in eeg.chanlocs]

        # TODO: Maybe taking the info dict from inst?
        info = _get_info(eeg)[0]
        mne.pick_info(info, np.round(eeg.icachansind).astype(int) - 1, copy=False)

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

        ica.info = info
        ica.pca_explained_variance_ = np.zeros(1,1)
        ica._update_ica_names()

        self.ica = ica

    def update_raw_from_eeglab(self, eeg):
        info = self.inst.info.copy()
        data = eeg.data / 1000000
        self.inst = mne.io.RawArray(data, info)
        
def eeg_from_matlab(eeg_struct):
    eeg = EEG()
    eeg.set_raw_from_eeglab(eeg_struct)
    return eeg
    

def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = dict[key]
    return dict        

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = OrderedDict()
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = elem
        else:
            dict[strg] = elem
    return dict