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
    epo_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="epo")
    epochs = mne.read_epochs(epo_filename, preload = True)

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
        Parallel(n_jobs=config["njobs"], prefer="threads")(delayed(average_epochs)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(delayed(average_epochs)(id) for id in ids)

if __name__ == '__main__':
    main()