from configuration import load_configuration

import utils

import mne
from mne import Report

from mne_bids import make_bids_basename, read_raw_bids
from mne_bids.utils import get_entity_vals

from collections import OrderedDict

from os.path import join
import argparse
from joblib import Parallel, delayed

import pandas as pd

import plotting

config = load_configuration()


def report_subject(id):

    report = Report(verbose=True)

    ## ICA ##

    # Load data, events and ica
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="raw", processing="prepared")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)
    ica_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ica")
    ica = mne.preprocessing.read_ica(ica_filename)

    # # Filter (like for ICA)
    # raw = raw.filter(
    #     l_freq=config["ica_l_freq"], h_freq=config["ica_h_freq"], fir_window="blackman")

    # # Epoch data
    # epochs = mne.Epochs(raw, events, config["events_dict"], picks = ["eeg", "eog"],
    #                     tmin=config["epoch_window"][0],
    #                     tmax=config["epoch_window"][1],
    #                     preload=True, baseline=None,
    #                     reject=None)
    ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')
    ica.info.set_montage(ten_twenty_montage, match_case=False)

    figures = ica.plot_components(cmap="rainbow", contours = 20, outlines = "head", topomap_args={"extrapolate":"head"}, show=False)
    report.add_figs_to_section(
        figures, captions=["ICA componnts overview"] * len(figures), section='ica')


    #besa_montage = mne.channels.read_custom_montage("matlab/standard-10-5-cap385.elp")


    # # Classification table
    # csv_filename = utils.get_derivative_file_name(
    #     config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")
    # labels = pd.read_csv(csv_filename)


    # #figures = [plotting.plot_ica_properties_and_labels(ica, epochs, n, cmap="rainbow")[0] for n in range(ica.n_components_)]

    # figures = []
    # for n in range(ica.n_components_):
    #     labels_names = labels.columns.tolist()
    #     labels_confidence = labels.iloc[n].tolist()
    #     figure = plotting.plot_ica_properties_and_labels(ica, epochs, n, labels_names, labels_confidence, topomap_args = {"cmap": "rainbow"})
    #     #figure = plotting.plot_ica_component_simple(ica, raw, n, labels_names, labels_confidence, cmap = "rainbow")
    #     figures.append(figure)

    # report.add_figs_to_section(
    #     figures, captions=["ICA componnts details"] * len(figures), section='ica')
    
    # Report evoked
    ave_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave")

    evokeds_list = mne.read_evokeds(ave_filename)
    evokeds_list_as_dict = {evoked.comment: evoked for evoked in evokeds_list}

    def difference_wave(evokeds_as_dict, conditions, grandaverage=True):

        try:
            out = [mne.combine_evoked([a, -b], "equal") for a, b in zip(
                evokeds_as_dict[conditions[0]], evokeds_as_dict[conditions[1]])]
        except TypeError:
            out = mne.combine_evoked( [evokeds_as_dict[conditions[0]], -evokeds_as_dict[conditions[1]]] , "equal")
 

        if grandaverage:
            return mne.grand_average(out)
        else:
            return out


    label = lambda condition_touple: str(condition_touple[0]) + " - " + str(condition_touple[1])

    for contrast in config["contrasts"]:
        if isinstance(contrast, list):
            plot_data = OrderedDict( [[label( contrast[0] ), difference_wave(evokeds_list_as_dict, contrast[0], False)],
                                      [label( contrast[1] ), difference_wave(evokeds_list_as_dict, contrast[1], False)]] )
            colors = config["alt_main_colors"]

        else:
            plot_data =  OrderedDict( [[str(contrast[0]), evokeds_list_as_dict[contrast[0]] ],
                                       [str(contrast[1]), evokeds_list_as_dict[contrast[1]] ]] )
            colors = config["main_colors"]

        figure = mne.viz.plot_compare_evokeds(
                plot_data, picks = ["Fz", "F4", "FC1", "FC2", "F3"], combine = "mean", colors=colors, show=False)

        report.add_figs_to_section(
            figure, captions = ' ', section = 'evoked')


        

    # Save report to disk
    report_filename = utils.get_derivative_report_file_name(
        config["bids_root_path"], id, config["pipeline_name"], suffix="report")

    report.save(report_filename, overwrite=True, open_browser=False)


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
