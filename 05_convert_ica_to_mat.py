from configuration import load_configuration
import mne

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed

from autoreject import Ransac, AutoReject

import utils

import numpy as np
from numpy.core.records import fromarrays
from scipy.io import savemat

config = load_configuration()


def convert_ica_to_mat(id):
    # Read raw file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="filtered")
    raw = mne.io.read_raw_fif(raw_filename, preload = True)
    raw = raw.pick(picks = "eeg")

        
    events = mne.make_fixed_length_events(raw, duration=1.0)
    epochs = mne.Epochs(raw, events, tmin=0.0, tmax=1.0, reject=None, baseline=None, preload=True)

    # Read ica file from disk
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")
    ica = mne.preprocessing.read_ica(ica_filename)

    # Create an EEGLAB EEG data structure

    ica_mixing_matrix = np.linalg.pinv(ica.mixing_matrix_)
    ica_pca_matrix = ica.pca_components_[:ica.n_components_]

    icawinv = np.linalg.pinv(np.matmul(ica_mixing_matrix, ica_pca_matrix))  # the mixing matrix

    icasphere = ica_pca_matrix 
    icaweights = ica_mixing_matrix




    eeglab_EEG = {}
    eeglab_EEG['data'] = np.transpose(epochs._data, [1,2,0]) * 1000
    eeglab_EEG['icaweights'] = icaweights
    eeglab_EEG['icasphere'] = icasphere
    eeglab_EEG['icawinv'] = icawinv
    eeglab_EEG["srate"] = raw.info["sfreq"]
    eeglab_EEG["nbchan"] = raw.info["nchan"]
    eeglab_EEG["times"] = epochs.times / 1000
    eeglab_EEG["trials"] = events.shape[0] - 1
    eeglab_EEG["xmin"] = 0
    eeglab_EEG["xmax"] = 1
    eeglab_EEG["ref"] = "average"
    eeglab_EEG["pnts"] = len(epochs.times)
    eeglab_EEG["setname"] = "Testset"
    eeglab_EEG["event"] = []
    eeglab_EEG["icaact"] = []
    eeglab_EEG["chanlocs"] =[{"X": ch["loc"][0], "Y": ch["loc"][1], "Z": ch["loc"][2], "labels": ch["ch_name"]} for ch in raw.info["chs"]]
    # >> EEG.chanlocs = [EEG.chanlocs{:}]

    mat_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".mat", suffix="ica-matlab")
    savemat(mat_filename, {'EEG': eeglab_EEG})

    #print(icaweights.shape)


def main():
    parser = argparse.ArgumentParser(description='Filter and epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                    help='IDs of subjects to process.', required=False)
    
    args = parser.parse_args()  
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(delayed(convert_ica_to_mat)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(delayed(convert_ica_to_mat)(id) for id in ids)

if __name__ == '__main__':
    main()

