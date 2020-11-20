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
from collections import OrderedDict 

import statsmodels.stats.anova

import seaborn as sns
import matplotlib.pyplot as plt

from functools import partial

config = None


def report_group():

    report = Report(verbose=True)

    # Get subjects ids
    ids = get_entity_vals(join(config["bids_root_path"], "derivatives"), "sub")
    #ids = ["001", "002", "003"]

    # Read files from disk
    ave_filenames = [utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave") for id in ids]
    all_evokeds = [mne.read_evokeds(ave_filename)
                                    for ave_filename in ave_filenames]

    # Report evoked

    # Turn list of dicts into dict of lists
    evokeds_list_as_dict = {key: []
        for key in config["conditions_of_interest"]}

    for evokeds_list in all_evokeds:
        for evoked in evokeds_list:
            evokeds_list_as_dict[evoked.comment].append(evoked)

    def difference_wave(evokeds_as_dict, conditions, grandaverage=False):

        out = [mne.combine_evoked([a, a], [1, -1]) for a, b in zip(
            evokeds_as_dict[conditions[0]], evokeds_as_dict[conditions[1]])]

        if grandaverage:
            return mne.grand_average(out)
        else:
            return out

    # # Find peak and find a window (±25ms) 
    diff = difference_wave(evokeds_list_as_dict, ("random/deviant", "random/standard"), grandaverage=True)
    peak_latency = diff.pick(picks="FZ").get_peak(tmin = .1, tmax = .2,  return_amplitude = True)[1]

    #peak_latency = .140
    peakwindow = (peak_latency-0.025, peak_latency+0.025)

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

        means_dict = OrderedDict( [[key, utils.get_mean_amplitudes(value, peakwindow, picks = ["FZ", "F4", "FC1", "FC2", "F3"])] for key,value in plot_data.items()])
        
        figure = plotting.compare_evokeds_boxplot(
                plot_data, means_dict = means_dict, picks = ["FZ", "F4", "FC1", "FC2", "F3"], combine = "mean", colors=colors, peakwindow = peakwindow, ci=False)
        
        # figure = plotting.compare_evokeds_seaborn(
        #         plot_data, picks = ["Fz"], colors1 = config["main_colors"], colors2= config["accent_colors"])

        report.add_figs_to_section(
            figure, captions = ' ', section = 'evoked')

    # Anova

    # conditions = {
    # #("predictable", "standard"): "predictable/4/standard",
    # ("predictable", "deviant"): "predictable/5/deviant",
    # ("random", "standard"): "random/4/standard",
    # ("random", "deviant"): "random/5/deviant"
    # }

    # avgfunc = partial(utils.get_mean_amplitudes, picks = ["FZ", "F4", "FC1", "FC2", "F3"])

    # rows = []
    # for key, condition in conditions.items():
    #     evokeds = evokeds_list_as_dict[condition]
    #     [rows.append(OrderedDict( [["Id", str(id)], ["Predictability", key[0]], ["Deviance", key[1]], ["MeanAmplitude",avgfunc(evoked, peakwindow)[0]]] )) for id, evoked in enumerate(evokeds)]

    # #%%
    # data = pd.DataFrame(rows)

    # anova = statsmodels.stats.anova.AnovaRM(data,"MeanAmplitude","Id", within = ["Predictability", "Deviance"])
    
    # #print(type(anova.fit().summary(returns="html")))
    
    # results = anova.fit().anova_table.to_html(classes="table table-hover")

    # report.add_htmls_to_section(results, captions = 'ANOVA', section = 'stats')
    # figure = plt.figure()
    # ax=figure.add_subplot()
    # sns.pointplot(data=data, ax=ax, x='Deviance', y='MeanAmplitude', hue='Predictability', dodge=True, markers=['o', 's'],
	#       capsize=.1, errwidth=1, palette=config["alt_main_colors"])

    # report.add_figs_to_section(figure, captions = 'ANOVA results (mean amplitude ~ deviance x predicatbility)', section = 'stats')
    # # Find peak and find a window (±25ms)
    # diff = difference_wave(evokeds_list_as_dict, ("random/deviant", "random/standard"), grandaverage=True)
    # peak = diff.pick(picks="FZ").get_peak(tmin = .1, tmax = .2,  return_amplitude = True)
    # peak_latency = peak[1]
    # peak_amplitude = peak[2]
    # peakwindow = (peak_latency-0.025, peak_latency+0.025)




    # fig = plt.figure()
    # ax = fig.subplots()

    # plotting.compare_evokeds(evokeds_list_as_dict, config["main_colors"], config["accent_colors"], ax=ax,
    #                             picks=["Fz"], shade = [peakwindow])
    # report.add_figs_to_section(
    #     figure, captions='Test', section='evoked')

    # # Plot peaks
    # for cond in ["random/deviant", "random/standard"]:
    #     amplitude = utils.get_mean_amplitude(evokeds_list_as_dict[], )
    #     ax.vlines(peak_latency, amplitude-.1,amplitude+.1)


    # # Save report to disk
    report_filename = utils.get_derivative_report_file_name(
        config["bids_root_path"], None, config["pipeline_name"], suffix="report")

    report.save(report_filename, overwrite = True)


def main():
    report_group()


if __name__ == '__main__':
    main()
