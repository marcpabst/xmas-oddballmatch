from configuration import load_configuration

import utils

import mne
from mne import Report

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed

config = load_configuration()


def make_report_subject(id):

    report = Report(verbose=True)

    # Report ICA
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")

    ica = mne.preprocessing.read_ica(ica_filename)

    figures = ica.plot_components()

    report.add_figs_to_section(
        figures, captions = ["ICA componnts overview"] * len(figures) , section='ica')


    # Report evoked
    ave_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave")

    evokeds_list = mne.read_evokeds(ave_filename)
    evokeds_list_as_dict = {evoked.comment: evoked for evoked in evokeds_list}

    figure = mne.viz.plot_compare_evokeds(evokeds_list_as_dict, picks="Fz")

    report.add_figs_to_section(
        figure, captions='All standards vs. all deviants (random condition)', section='evoked')

    # Save report to disk
    report_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".html", suffix="report")

    report.save(report_filename, overwrite=True)


def main():
    parser = argparse.ArgumentParser(description='Filter and epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(make_report_subject)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=config["njobs"], prefer="threads")(
            delayed(make_report_subject)(id) for id in ids)


if __name__ == '__main__':
    main()
