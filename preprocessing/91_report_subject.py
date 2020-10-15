from ...configuration.configuration import load_configuration
from mne_bids.utils import get_entity_vals

import argparse

import time

import parsl
from parsl.app.app import python_app
from parsl_config import pconfig

config = load_configuration()

@python_app
def report_subject(id, config):
    import utils
    import mne
    from mne import Report
    from collections import OrderedDict
    from os.path import join
    import pandas as pd
    import plotting


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

    besa_montage = mne.channels.read_custom_montage("standard-10-5-cap385.elp")
    ica.info.set_montage(besa_montage, match_case=False)

    # Classification table
    csv_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".csv", suffix="ica-matlab")
    labels = pd.read_csv(csv_filename)
    labels_names = labels.idxmax(axis=1).tolist()

    ica._ica_names = ['No.{} ({})'.format(ii, labels_names[ii]) for ii in range(ica.n_components_)]
    figures = ica.plot_components(cmap="rainbow", contours = 5, show=False, picks="all")
    report.add_figs_to_section(
        figures, captions="ICA componnts overview", section='ica')


    # # PLOT EVOKED RESPONSES

    # # COMPARE NOPATTERN DEVIANTS VS NOPATTERN STANDARDS
    #             evokeds_as_dict[conditions[0]], evokeds_as_dict[conditions[1]])]
    #     except TypeError:
    #         out = mne.combine_evoked( [evokeds_as_dict[conditions[0]], -evokeds_as_dict[conditions[1]]] , "equal")
 

    #     if grandaverage:
    #         return mne.grand_average(out)
    #     else:
    #         return out


    # label = lambda condition_touple: str(condition_touple[0]) + " - " + str(condition_touple[1])

    # for contrast in config["contrasts"]:
    #     if isinstance(contrast, list):
    #         plot_data = OrderedDict( [[label( contrast[0] ), difference_wave(evokeds_list_as_dict, contrast[0], False)],
    #                                   [label( contrast[1] ), difference_wave(evokeds_list_as_dict, contrast[1], False)]] )
    #         colors = config["alt_main_colors"]

    #     else:
    #         plot_data =  OrderedDict( [[str(contrast[0]), evokeds_list_as_dict[contrast[0]] ],
    #                                    [str(contrast[1]), evokeds_list_as_dict[contrast[1]] ]] )
    #         colors = config["main_colors"]

    #     figure = mne.viz.plot_compare_evokeds(
    #             plot_data, picks = ["FZ", "F4", "FC1", "FC2", "F3"], combine = "mean", colors=colors, show=False)

    #     report.add_figs_to_section(
    #         figure, captions = ' ', section = 'evoked')


        

    # Save report to disk
    report_filename = utils.get_derivative_report_file_name(
        config["bids_root_path"], id, config["pipeline_name"], suffix="report")

    report.save(report_filename, overwrite=True, open_browser=False)


def main():
    parser = argparse.ArgumentParser(description='Epoch data.')
    parser.add_argument('-s', '--subjects', nargs='+', type=str,
                        help='IDs of subjects to process.', required=False)

    args = parser.parse_args()
    
    parsl.load(pconfig)
    parsl.set_stream_logger()

    if args.subjects:
        tasks = [report_subject(id, config) for id in args.subjects]
    else:
        ids = get_entity_vals(config["bids_root_path"], "sub")
        tasks = [report_subject(id, config) for id in ids]

    while not all([i.done() for i in tasks]):
        time.sleep(1)


if __name__ == '__main__':
    main()
