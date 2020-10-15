from configuration import load_configuration
import mne
from mne_bids.config import BIDS_VERSION
from mne_bids.utils import _write_json
from mne_bids import make_bids_basename, write_raw_bids

from os.path import join
import argparse
from joblib import Parallel, delayed

config = load_configuration()


def convert_to_bids(id):
    """
    Prepare data and convert into BIDS format.
    """
    filename = config["raw_path"].format(id=id, preload=True)
    # Read file from disk (excluding flat electrode)
    raw = mne.io.read_raw_bdf(filename, preload=False)
    # Read events
    events = mne.find_events(raw, shortest_event=1)
    # Convert data to BIDS format
    subject_id = '{id:03d}'.format(id=id)
    bids_basename = make_bids_basename(
        subject=subject_id, task=config["task_name"])
    write_raw_bids(raw, bids_basename, config["bids_root_path"], event_id=config["events_dict"],
                   events_data=events, overwrite=True)


def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=int,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(convert_to_bids)(id) for id in args.subjects)
    else:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(convert_to_bids)(id) for id in config["raw_ids"])


if __name__ == '__main__':
    main()
