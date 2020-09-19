###########################################
###### Label Independant Components #######
###########################################

from configuration import load_configuration
import mne

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed
import os

from autoreject import Ransac, AutoReject

import utils

import numpy as np
from numpy.core.records import fromarrays
from scipy.io import savemat

import subprocess

config = load_configuration()


def label_ics(id):
    # Read raw file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)
    raw = raw.pick(picks=["eeg", "eog"])

    # Filter (like for ICA)
    raw = raw.filter(
        l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window="blackman")

    # Epoch data
    epochs = mne.Epochs(raw, events, config["events_dict"], picks = ["eeg", "eog"],
                        tmin=config["epoch_window"][0],
                        tmax=config["epoch_window"][1],
                        preload=True,
                        baseline=None, reject=None)

    # Read ica file from disk
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")
    ica = mne.preprocessing.read_ica(ica_filename)

    # Drop bad channels
    bad_channels = list(set(epochs.info["ch_names"]) -  set(ica.info["ch_names"]))
    epochs = epochs.drop_channels(bad_channels)

    # Create an EEGLAB EEG data structure
    ica_unmixing_matrix = np.linalg.pinv(ica.mixing_matrix_)
    ica_pca_matrix = ica.pca_components_[:ica.n_components_]

    icawinv = np.linalg.pinv(np.matmul(ica_unmixing_matrix, ica_pca_matrix))
    icasphere = ica_pca_matrix
    icaweights = ica_unmixing_matrix

    eeglab_EEG = {}
    eeglab_EEG['data'] = np.transpose(epochs._data, [1, 2, 0]) * 1000
    eeglab_EEG['icaweights'] = icaweights
    eeglab_EEG['icasphere'] = icasphere
    eeglab_EEG['icawinv'] = icawinv
    eeglab_EEG["srate"] = epochs.info["sfreq"]
    eeglab_EEG["nbchan"] = epochs.info["nchan"]
    eeglab_EEG["times"] = epochs.times / 1000
    eeglab_EEG["trials"] = events.shape[0] - 1
    eeglab_EEG["xmin"] = 0
    eeglab_EEG["xmax"] = 1
    eeglab_EEG["ref"] = "average"
    eeglab_EEG["pnts"] = len(epochs.times)
    eeglab_EEG["setname"] = "Testset"
    eeglab_EEG["event"] = []
    eeglab_EEG["icaact"] = []
    # eeglab_EEG["chanlocs"] = [{"X": ch["loc"][1], "Y": -ch["loc"][0],
    #                            "Z": ch["loc"][2], "labels": ch["ch_name"]} for ch in epochs.info["chs"]]
    eeglab_EEG["chanlocs"] = [{"labels": ch["ch_name"]} for ch in epochs.info["chs"]]

    mat_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".mat", suffix="ica-matlab")
    savemat(mat_filename, {'EEG': eeglab_EEG})

    
    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")

    # Calling Matlab through shell
    process = subprocess.Popen(['matlab', '-nodisplay', '-batch',
                                'addpath("matlab/", genpath("matlab/eeglab")); label_ics("'+mat_filename+'", "'+csv_filename+'"); exit();']).wait()
    os.remove(mat_filename)

def main():
    parser = argparse.ArgumentParser(description='Filter and epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(label_ics)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(label_ics)(id) for id in ids)


if __name__ == '__main__':
    main()
