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


def average_epochs(id):

    # Read file from disk
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="cleaned")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

    # Epoch data
    epochs = mne.Epochs(raw, events, config["events_dict"],
                        tmin=config["epoch_window"][0],
                        tmax=config["epoch_window"][1],
                        baseline=config["baseline_winow"],
                        reject={"eog": 100e-4})

    evokeds_list = []
    for condition in config["conditions_of_interest"]:
        evoked = epochs[condition].average()
        evoked.comment = condition
        evokeds_list.append(evoked)

    ave_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave")

    mne.write_evokeds(ave_filename, evokeds_list)


def main():
    parser = argparse.ArgumentParser(description='Filter and epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(average_epochs)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(average_epochs)(id) for id in ids)


if __name__ == '__main__':
    main()
