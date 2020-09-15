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

import seab

import plotting

config = load_configuration()


def report_group():

    report = Report(verbose=True)

    # Get subjects ids
    ids = get_entity_vals(join(config["bids_root_path"], "derivatives"), "sub")
    ids = ["001","002","003"]

    # Read files from disk
    ave_filenames = [utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave") for id in ids]
    all_evokeds = [mne.read_evokeds(ave_filename) for ave_filename in ave_filenames]

    # Report evoked

    evokeds_list_as_dict = {}
    evokeds_list_as_dict["random/deviant"] = []
    evokeds_list_as_dict["random/standard"] = []

    for evokeds_list in all_evokeds:
        for evoked in evokeds_list:
            if evoked.comment == "random/deviant" or evoked.comment == "random/standard":
                evokeds_list_as_dict[evoked.comment].append(evoked)

    figure = mne.viz.plot_compare_evokeds(evokeds_list_as_dict, picks=["F3", "Fz", "F4", "FC1", "FC2"], combine = "mean")
    report.add_figs_to_section(
        figure, captions='All standards vs. all deviants (random condition)', section='evoked')


    def difference_wave(evokeds_as_dict, conditions, grandaverage = False):
        
        out = [mne.combine_evoked([a, -b], "equal") for a,b in zip(evokeds_as_dict[conditions[0]], evokeds_as_dict[conditions[1]])]

        if grandaverage:
            return mne.grand_average(out)
        else:
            return out

    diff1 = difference_wave(evokeds_list_as_dict, ("random/deviant", "random/standard"), True)
    figure = mne.viz.plot_evoked(diff1, picks=["F3", "Fz", "F4", "FC1", "FC2"])
    report.add_figs_to_section(
        figure, captions='All standards vs. all deviants (random condition)', section='evoked')


    # Find peak and find a window (±25ms) 
    diff = difference_wave(evokeds_list_as_dict, ("random/deviant", "random/standard"), grandaverage=True)
    peak = diff.pick(picks="Fz").get_peak(tmin = .1, tmax = .2,  return_amplitude = True)
    peak_latency = peak[1]
    peak_amplitude = peak[2]
    peakwindow = (peak_latency-0.025, peak_latency+0.025)




    fig = plt.figure()
    ax = fig.subplots()

    plotting.compare_evokeds(evokeds_list_as_dict, config["main_colors"], config["accent_colors"], ax=ax,
                                picks=["Fz"], shade = [peakwindow])
    report.add_figs_to_section(
        figure, captions='Test', section='evoked')

    # Plot peaks
    for cond in ["random/deviant", "random/standard"]:
        amplitude = utils.get_mean_amplitude(evokeds_list_as_dict[], )
        ax.vlines(peak_latency, amplitude-.1,amplitude+.1)


    # Save report to disk
    report_filename = utils.get_derivative_report_file_name(
        config["bids_root_path"], None, config["pipeline_name"], suffix="report")

    report.save(report_filename, overwrite=True)


def main():
    report_group()


if __name__ == '__main__':
    main()
