from configuration import load_configuration

import utils

import mne
from mne import Report

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from os.path import join
import argparse
from joblib import Parallel, delayed

import pandas as pd

import plotting

config = load_configuration()


def report_subject(id):

    report = Report(verbose=True)

    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing = "prepared")
    raw = mne.io.read_raw_fif(raw_filename)

    ### Report ICA ###

    # Overview
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")

    ica = mne.preprocessing.read_ica(ica_filename)

    figures = ica.plot_components(cmap="rainbow")
    report.add_figs_to_section(
        figures, captions=["ICA componnts overview"] * len(figures), section='ica')

    # Classification table
    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")
    labels = pd.read_csv(csv_filename)

    figures = []
    for n in range(0,ica.n_components_):
        labels_names = labels.columns.tolist()
        labels_confidence = labels.iloc[n].tolist()
        figure = plotting.plot_ica_component_simple(ica, raw, n, labels_names, labels_confidence, cmap = "rainbow")
        figures.append(figure)

    report.add_figs_to_section(
        figures, captions=["ICA componnts details"] * len(figures), section='ica')
    
    # Report evoked
    ave_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave")

    evokeds_list = mne.read_evokeds(ave_filename)
    evokeds_list_as_dict = {evoked.comment: evoked for evoked in evokeds_list}


    figure = mne.viz.plot_compare_evokeds(evokeds_list_as_dict, picks="Fz")
    report.add_figs_to_section(
        figure, captions='All standards vs. all deviants (random condition): Fz', section='evoked')

    #  Pool 
    figure = mne.viz.plot_compare_evokeds(evokeds_list_as_dict, picks=["F3", "Fz", "F4", "FC1", "FC2"], combine = "mean")
    report.add_figs_to_section(
        figure, captions='All standards vs. all deviants (random condition): Pooled F3, Fz, F4, FC1, FC2', section='evoked')

    figure = plotting.compare_evokeds(evokeds_list_as_dict, config["main_colors"], config["accent_colors"], picks=["Fz"])
    report.add_figs_to_section(
        figure, captions='Test', section='evoked')

        

    # Save report to disk
    report_filename = utils.get_derivative_report_file_name(
        config["bids_root_path"], id, config["pipeline_name"], suffix="report")

    report.save(report_filename, overwrite=True)


def main():
    parser = argparse.ArgumentParser(description='Filter and epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    if args.subjects:
        Parallel(n_jobs=1, prefer="threads")(
            delayed(report_subject)(id) for id in args.subjects)
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        Parallel(n_jobs=1, prefer="threads")(
            delayed(report_subject)(id) for id in ids)


if __name__ == '__main__':
    main()
