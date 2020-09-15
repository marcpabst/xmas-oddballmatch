from configuration import load_configuration
import mne

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed

from autoreject import Ransac, AutoReject

import utils

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
    raw = utils.cut_raw_blocks(
        raw, events, config["events_dict"], "begin", "end")

    # Remove line noise using ZapLine
    if config["line_freq"] is not None:
        raw = utils.apply_zapline(
            raw, config["line_freq"], picks=["eeg"], nremove=3)

    # Filter
    raw = raw.filter(
        l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window="blackman")

    # Cut continous data into arbitrary epochs of 1 s
    events = mne.make_fixed_length_events(raw, duration=1.0)
    epochs = mne.Epochs(raw, events, tmin=0.0, tmax=1.0,
                        reject=None, baseline=None, preload=True)

    # Identify bad channels using RANSAC
    ransac = Ransac(n_jobs=config["njobs2"], verbose='progressbar')
    ransac.fit(epochs)

    epochs.info['bads'] = ransac.bad_chs_
    n_bad_channels = len(epochs.info['bads'])
    n_all_channels = len(mne.channel_indices_by_type(epochs.info)["eeg"]) + len(mne.channel_indices_by_type(epochs.info)["eog"])

    # Drop bad channels
    epochs = epochs.drop_channels(epochs.info['bads'])

    # Downsample
    if config["ica_downsample_freq"] is not None:
        epochs = epochs.resample(config["ica_downsample_freq"])

    # Create ICA
    n_pca_components = n_all_channels - n_bad_channels - 1
    ica = mne.preprocessing.ICA(n_components=n_pca_components, method="picard",
                                fit_params=None, random_state=config["random_state"])

    # Fit ICA
    ica.fit(epochs, picks=["eeg", "eog"], reject={
            "data": config["ica_diff_criterion"]})

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
