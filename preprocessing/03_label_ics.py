###########################################
###### Label Independant Components #######
###########################################

from ...configuration.configuration import load_configuration
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

from interop2 import EEG, EEGlab

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

    # # Create an EEGLAB EEG data structure
    # ica_unmixing_matrix = np.linalg.pinv(ica.mixing_matrix_)
    # ica_pca_matrix = ica.pca_components_[:ica.n_components_]

    # icawinv = ica.mixing_matrix_
    # icasphere = ica.pca_components_
    # icaweights =  ica.unmixing_matrix_

    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")

    
    # Run IClabel using matlab
    with EEGlab("/share/projects/pabst/xmasoddballmatch/xmas-oddballmatch/matlab/eeglab") as eeglab, EEG(inst=epochs, ica=ica) as eeg:
        #eeg = eeglab.pop_chanedit(eeg, 'lookup', 'matlab/standard-10-5-cap385.elp')
        eeglab.label_ics(eeg, csv_filename)
        

    
  
    # Calling Matlab through shell
   ## process = subprocess.Popen(['matlab', '-nodisplay', '-batch',
    #                            'addpath("matlab/", genpath("matlab/eeglab")); label_ics("'+mat_filename+'", "'+csv_filename+'"); exit();']).wait()
    #os.remove(mat_filename)

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
