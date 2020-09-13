from configuration import load_configuration
import mne

from mne_bids import make_bids_basename, read_raw_bids, write_raw_bids
from mne_bids.utils import get_entity_vals

import argparse
from joblib import Parallel, delayed

from autoreject import Ransac, AutoReject

import utils

config = load_configuration()


def prepare_data(id):
    # Read file from disk
    bids_basename = make_bids_basename(subject=id, task=config["task_name"])
    bids_filename = bids_basename + "_{}.bdf".format("eeg")
    raw = read_raw_bids(bids_filename, config["bids_root_path"])
    events = mne.find_events(raw, initial_event=True, shortest_event=1)

    # Drop EXG8
    raw = raw.drop_channels(["EXG8"])

    # Rename channels to match MNE's montage
    raw = raw.rename_channels(
        {"FZ": "Fz", "PZ": "Pz", "OZ": "Oz", "CZ": "Cz", "FP2": "Fp2"})

    # Re-Reference
    raw = raw.set_eeg_reference("average")

    # Assign correct channel types
    raw = raw.set_channel_types(
        {"SO2": "eog", "IO2": "eog", "LO1": "eog", "LO2": "eog", "Nose": "misc"})

    # Load and apply standard 10-20 montage
    ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
    raw = raw.set_montage(ten_twenty_montage)

    # Write to file
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    raw.save(raw_filename, overwrite=True)
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    mne.write_events(events_filename, events)


def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(prepare_data)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(prepare_data)(id) for id in ids)


if __name__ == '__main__':
    main()
