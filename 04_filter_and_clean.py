###########################################
########## Filter and clean data ##########
###########################################

from configuration import load_configuration
import mne

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed

from autoreject import Ransac, AutoReject

import pandas as pd

import utils

config = load_configuration()


def filter_and_clean(id):
    # Read file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload = True)
    events = mne.read_events(events_filename)

    # Bipolarize EOG
    raw = mne.set_bipolar_reference(raw, "SO2", "IO2", "vEOG")
    raw = mne.set_bipolar_reference(raw, "LO1", "LO2", "hEOG")

    # Re-reference
    raw = raw.set_eeg_reference(["Nose"])

    # Merge events REALY?
    events = mne.merge_events(events, [41, 98], 41)
    events = mne.merge_events(events, [52, 99], 52)

    # Filter data
    raw = raw.filter(l_freq = config["l_freq"], h_freq = config["h_freq"], fir_window = config["fir_window"])

    # Clean data
    
    # Read ica, and labels from disk
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")
    ica = mne.preprocessing.read_ica(ica_filename)
    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")
    labels = pd.read_csv(csv_filename)

    labels_names = labels.idxmax(axis=1).tolist()
    labels_confidence = labels.max(axis=1).tolist()
    exclude_idx = [i for i, name in enumerate(labels_names) if name != "Brain" and name != "Other"]

    # Apply ICA to data, but zeroing-out non-brain components
    raw = ica.apply(raw, exclude= exclude_idx)
    
    # Write to file
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    raw.save(raw_filename, overwrite = True)

    

def main():
    parser = argparse.ArgumentParser(description='Filter and clean data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                    help='IDs of subjects to process.', required=False)
    
    args = parser.parse_args()  
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(delayed(filter_and_clean)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(delayed(filter_and_clean)(id) for id in ids)

if __name__ == '__main__':
    main()