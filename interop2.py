#from pymatbridge import Matlab
import subprocess
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

import random
import string

import warnings

from tempfile import TemporaryDirectory




class EEGlab():
    """
    Wrapper object for EEGLAB.
    """
    session = None
    tmp_dir = None
    eeglab_dir = None

    def __init__(self, dir, tdir):
        rnd = ''.join(random.choice(string.ascii_lowercase) for i in range(15))
        self.tmp_dir = TemporaryDirectory()
        #self.session = Matlab()  
        self.eeglab_dir = dir
        #self.session.start()
        #self.session.run_code("cd "+self.tmp_dir.name)
        #self.session.run_func("addpath", dir)
        #self.session.run_code("eeglab")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        #self.session.run_func("exit")
        self.tmp_dir.cleanup()

    def __getattr__(self, name):
        def wrapper(*args):
            for arg in args:
                print("ARG: ", type(arg))

            if isinstance(args[0], EEG):
                new_args = list(args)
                new_args[0] = args[0].to_dict()
            else:
                new_args = args

            
            #r = getattr(self.session, str(name))()
            #r = self.session.run_func(name, *args)
            # save to temp file
            fpath = join(self.tmp_dir.name, "tmp.mat")
            savemat(fpath, {"ARGS": new_args})
            
            command = "matlab -nodisplay -r \""
            command +=  "addpath('{}');".format(self.eeglab_dir)
            command +=  "eeglab;"
            command +=  "load('{}');".format(fpath)
            command += "RES = {}(ARGS{{:}});".format(name)
            command += "save('{}', 'RES');".format(fpath)
            command += "exit();\""

            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            while process.poll() is None:
                output = process.stdout.readline()
                if process.poll() is not None and output == '':
                    break
                if output:
                    print (output.strip())


            r = loadmat(fpath)["RES"]

        
            
            if isinstance(args[0], EEG):
                return EEG(eeg=r)
            else:
                return r

        return wrapper


class EEG(object):
    """
    Wraps an MNE's Raw instance and optionally instances of ICA, etc.
    """

    _eeg = None
    _org_info = None

    def __init__(self, inst=None, ica=None, eeg=None):
        if eeg is not None:
            self._eeg = eeg
            return

        self._org_info = inst.info
        self._eeg = OrderedDict()

        if isinstance(inst, mne.io.Raw):
            data = inst.get_data()
            self._eeg["data"] = np.double(data * 1000000)
            self._eeg["trials"] = np.double(1)
        elif isinstance(inst, mne.epochs.Epochs):
            self._eeg["data"] =  np.double(np.transpose(inst.get_data(), [1, 2, 0]) * 1000000)
            self._eeg["trials"] = np.double(len(inst))
       
        self._eeg["srate"] =  np.double(inst.info["sfreq"])
        self._eeg["nbchan"] =  np.double(inst.info["nchan"])
        self._eeg["times"] =  np.double(inst.times / 1000)
        self._eeg["xmin"] = np.double(inst.times[0])
        self._eeg["xmax"] = np.double(inst.times[-1])
        self._eeg["ref"] =  "average"
        self._eeg["pnts"] = np.double(len(inst.times))
        self._eeg["setname"] = "n/a"
        self._eeg["event"] =  []
        self._eeg["icaact"] = []
        self._eeg["icasphere"] =  []
        self._eeg["icaweights"] = []
        self._eeg["icawinv"] =  []
        self._eeg["chanlocs"] = fromarrays([[ch["ch_name"] for ch in inst.info["chs"]]], names=['labels'])

        if ica is not None:
            n_ch = len(ica.ch_names)
            n_components = ica.n_components
            
            if n_components < n_ch:
                # When PCA reduction is used in EEGLAB, runica returns
                # weights= weights*sphere*eigenvectors(:,1:ncomps)';
                # sphere = eye(urchans), so let's use SVD to get our square
                # weights matrix (u * s) and our PCA vectors (v) back
                raise NotImplementedError("PCA reduction is currently not supported.")
                self._eeg["icaweights"] = unmixing_matrix_ * sphere * np.eye()
                self._eeg["icasphere"] = np.eye(n_ch)
                u, s, v = _safe_svd(eeg.icaweights, full_matrices=False)
                ica.unmixing_matrix_ = u * s
                ica.pca_components_ = v
            else:
                self._eeg["icaweights"] = ica.unmixing_matrix_
                self._eeg["icasphere"] = ica.pca_components_
                self._eeg["icawinv"] = np.linalg.pinv(np.matmul(ica.unmixing_matrix_, ica.pca_components_))


    def __setitem__(self, name, data):
        _eeg[name] = data

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

    def __getitem__(self, name):
        return self._eeg[name]

    def to_dict(self):
        return self._eeg

    def items(self):
        self.to_dict().items()

    def update(self, eeg):
        self._eeg = eeg
    
    def get_ica(self):
        eeg = self._eeg
        eeg.chanlocs = [{f: getattr(chl, f) for f in chl._fieldnames} for chl in eeg.chanlocs]
        info = _get_info(eeg)[0]
        print(info)
        #mne.pick_info(info, np.round(eeg.icachansind).astype(int) - 1, copy=False)

        n_components = eeg.icaweights.shape[0]

        ica = mne.preprocessing.ICA(method='imported_eeglab', n_components=n_components)
        ica.info = info

        ica.current_fit = "eeglab"
        ica.ch_names = info["ch_names"]
        ica.n_pca_components = None
        ica.max_pca_components = n_components
        ica.n_components_ = n_components

        ica.pre_whitener_ = np.ones((len(eeg.icachansind), 1))
        ica.pca_mean_ = np.zeros(len(eeg.icachansind))
        
        n_ch = len(ica.ch_names)

        if n_components < ica.n_ch:
            u, s, v = _safe_svd(eeg.icaweights, full_matrices=False)
            ica.unmixing_matrix_ = u * s
            ica.pca_components_ = v
        else:
            ica.unmixing_matrix_ = eeg.icaweights
            ica.pca_components_ = eeg.icasphere
            ica.mixing_matrix_ = np.linalg.pinv(ica.pca_components_) @ eeg.icawinv

        ica.pca_explained_variance_ = np.zeros((1,1))
        ica._update_ica_names()
     
        return ica

    def get_instance(self):
        eeg = self._eeg
        info = self._org_info
        data = eeg.data / 1000000
        return mne.io.RawArray(data, info)
        
    

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



