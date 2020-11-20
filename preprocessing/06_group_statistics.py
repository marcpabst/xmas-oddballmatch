from configuration import load_configuration
import mne

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed

from autoreject import Ransac, AutoReject

import utils

config = None


def group_statistics():
    # Get subjects ids
    ids = get_entity_vals(join(config["bids_root_path"], "derivatives"), "sub")

    # Read files from disk
    evoked_filenames = [utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="cleaned") for id in ids]

    evokeds = [mne.read_evokeds(evoked_filename) for evoked_filename in evoked_filenames]



def main():
    group_statistics()


if __name__ == '__main__':
    main()
