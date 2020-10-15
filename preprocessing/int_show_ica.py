from ...configuration.configuration import load_configuration
import mne

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed

from autoreject import Ransac, AutoReject, get_rejection_threshold

import utils
import numpy as np
from numpy.core.records import fromarrays
from scipy.io import savemat

from interop2 import EEG, EEGlab

config = load_configuration()


def show_ica(id):

    # Read file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

    # Cut non-block data
    # raw = utils.cut_raw_blocks(
    #    raw, events, config["events_dict"], "begin", "end")

    # Remove line noise using ZapLine
    if config["line_freq"] is not None:
        raw = utils.apply_zapline(
            raw, config["line_freq"], picks=["eeg"], nremove=3)

    # Filter
    raw = raw.filter(
        l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window=config["ica_fir_window"])


    # Downsample
    if config["ica_downsample_freq"] is not None:
        raw = raw.resample(config["ica_downsample_freq"])
  
    # Cut continous data into arbitrary epochs of 1 s
    events = mne.make_fixed_length_events(raw, duration=config["ica_step"])
    epochs = mne.Epochs(raw, events, tmin=0.0, tmax=config["ica_step"], picks=[
                        "eeg", "eog"], baseline=None, preload=True, reject=None)

    # Downsample
    if config["ica_downsample_freq"] is not None:
        epochs = epochs.resample(config["ica_downsample_freq"])

    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")
    ica = mne.preprocessing.ica.read_ica(ica_filename)

    ica.plot_components(inst=epochs)



def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    ids = get_entity_vals(config["bids_root_path"], "sub")
    show_ica(ids[0]) 
 

if __name__ == '__main__':
    main()
