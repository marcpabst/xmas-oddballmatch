###########################################
###### Label Independant Components #######
###########################################

from ...configuration.configuration import load_configuration

from os.path import join
import argparse
from joblib import Parallel, delayed
import os

import utils


config = load_configuration()


def cleanup(id):
    
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")
    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")

    os.remove(raw_filename)
    os.remove(events_filename)
    os.remove(ica_filename)
    os.remove(csv_filename)

def main():
    parser = argparse.ArgumentParser(description='Filter and epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(cleanup)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(cleanup)(id) for id in ids)


if __name__ == '__main__':
    main()
