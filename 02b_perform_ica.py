from configuration import load_configuration
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


def perform_ica(id):

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

    # Running PREP
    prep_params = {
        "ref_chs": "eeg",
        "reref_chs": ["eeg", "eog"],
        "line_freqs": np.arange(config["line_freq"], raw.info["sfreq"] / 2, config["line_freq"]),
    }

    prep = PrepPipeline(raw, prep_params, raw.get_montage())
    prep.fit()
  
    # Filter
    raw = raw.filter(
        l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window=config["ica_fir_window"])

    # Downsample
    if config["ica_downsample_freq"] is not None:
        raw = raw.resample(config["ica_downsample_freq"])

    # Run ASR
    raw = utils.apply_asr(raw)

    # Create ICA
    n_channels = len(raw.info["ch_names"])
    n_components = n_channels - len(prep.interpolated_channels())
    ica = mne.preprocessing.ICA(n_components=, method="picard",
                              random_state=config["random_state"], max_iter=600)
    # Fit ICA
    ica.fit(raw, picks=["eeg", "eog"], reject=rejection_thresholds)

    # Save ICA to disk
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")

    ica.save(ica_filename)


def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(perform_ica)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(perform_ica)(id) for id in ids)


if __name__ == '__main__':
    main()
