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

    # Load and apply standard 10-20 montage
    #ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
    #raw = raw.set_montage(ten_twenty_montage)

    # Cut non-block data
    raw = utils.cut_raw_blocks(
        raw, events, config["events_dict"], "begin", "end")

    # Remove line noise using ZapLine
    raw = utils.apply_zapline(
        raw, config["line_freq"], picks=["eeg"], nremove=3)

    # Filter
    raw = raw.filter(l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window="blackman")

    # Plot
    #fig = mne.viz.plot_raw_psd(raw)
    #report.add_section(title = "PSD after Line Noise Removal (ZapLine) and Filtering", plot = fig)

    # Cut continous data into arbitrary epochs of 1 s
    events = mne.make_fixed_length_events(raw, duration=1.0)
    epochs = mne.Epochs(raw, events, tmin=0.0, tmax=1.0,
                        reject=None, baseline=None, preload=True)

    # Identify bad channels using RANSAC
    ransac = Ransac(n_jobs=config["njobs2"], verbose='progressbar')
    ransac.fit(epochs)
    raw.info['bads'] = ransac.bad_chs_
    n_bad_channels = len(raw.info['bads'])
    n_all_channels = len(mne.channel_indices_by_type(raw.info)["eeg"])

    # Interpolate bad channels
    epochs = epochs.interpolate_bads(reset_bads=True)

    # Create ICA
    n_pca_components = n_all_channels-n_bad_channels-1
    ica = mne.preprocessing.ICA(n_components=n_pca_components, method="picard",
                                fit_params=None, random_state=config["random_state"])

    # Fit ICA
    ica.fit(epochs, picks=["eeg"], reject={
            "eeg": config["ica_diff_criterion"]})

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
