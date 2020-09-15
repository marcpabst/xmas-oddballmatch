import mne
import matplotlib
import numpy as np
from copy import deepcopy
from numbers import Integral
import matplotlib.pyplot as plt


class AnchoredVScaleBar(matplotlib.offsetbox.AnchoredOffsetbox):
    """ size: length of bar in data units
        extent : height of bar ends in axes units """
    def __init__(self, size=1, extent = 0.03, label="", loc=2, ax=None,
                 pad=0.4, borderpad=0.5, ppad = 0, sep=2, prop=None, 
                 frameon=True, linekw={}, **kwargs):
        if not ax:
            ax = plt.gca()
        trans = ax.get_yaxis_transform()
        size_bar = matplotlib.offsetbox.AuxTransformBox(trans)
        line = Line2D([0,0], [size,0], **linekw)
        hline1 = Line2D([-extent/2.,extent/2.],[0,0], **linekw)
        hline2 = Line2D([-extent/2.,extent/2.],[size,size], **linekw)
        size_bar.add_artist(line)
        size_bar.add_artist(hline1)
        size_bar.add_artist(hline2)
        txt = matplotlib.offsetbox.TextArea(label, minimumdescent=False)
        self.vpac = matplotlib.offsetbox.HPacker(children=[size_bar,txt],  
                                 align="center", pad=ppad, sep=sep) 
        matplotlib.offsetbox.AnchoredOffsetbox.__init__(self, loc, pad=pad, 
                 borderpad=borderpad, child=self.vpac, prop=prop, frameon=frameon,
                 **kwargs)


def compare_evokeds(evoked_dict, colors1, colors2, picks = "data", ax = None, shade = None):

    if ax == None:
        fig = plt.figure()
        ax = fig.subplots()


    for i, (condition, evoked_list) in enumerate(evoked_dict.items()):
        try:
            _evoked_list = [evoked.pick_channels(picks) for evoked in evoked_list]
            grand_avg = mne.grand_average(_evoked_list)
        except TypeError:
            grand_avg = evoked_list.pick_channels(picks)

        dat = grand_avg.data.T * 1000000
        times = grand_avg.times

        ax.plot(times, dat, zorder=1000, label=condition, clip_on=False, color = colors1[i] )

       

    ob = AnchoredVScaleBar(size=.5, label="50 µV", loc=2, frameon=False,
                    pad=0.6, sep=4) 
    
    ax.add_artist(ob)
    

    ax.set_xlabel('Time (s)')
    ax.axhline(y=0, xmin=0, xmax=1, color="black", alpha=.4)
    yabs_max = abs(max(ax.get_ylim(), key=abs))
    ax.set_ylim(-yabs_max, yabs_max)
    ax.get_yaxis().set_visible(False)

    ax.set_xlim(-.3, .3)

    ax.spines['left'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    

    xticks = ax.xaxis.get_majorticklocs()
    ax.spines['bottom'].set_bounds(xticks[0], xticks[-1])

    if shade is not None:
        for s in shade:
            ax.axvspan(s[0], s[1], alpha=0.5, color='red')
            

    

    if fig != None:
        return fig

        
        #     # plot the confidence interval if available
        #     if ci_dict.get(condition, None) is not None:
        #         ci_ = ci_dict[condition]
        #         ax.fill_between(times, ci_[0].flatten(), ci_[1].flatten(),
        #                         zorder=9, color=styles[condition]['color_ci'],
        #                         alpha=0.5, clip_on=False)
        # if topo:
        #     ax.text(-.1, 1, title, transform=ax.transAxes)
        # else:
        #     ax.set_title(title)

def plot_ica_component_simple(ica, inst, pick, class_labels, class_percent, cmap = None, axs = None):
    if axs == None:
        fig = plt.figure(figsize=(20,4))
        gs = fig.add_gridspec(2, 6, wspace=.5, hspace=.4)
        axs = (fig.add_subplot(gs[:, 0:2]),  
                fig.add_subplot(gs[0, 2:5]),
                fig.add_subplot(gs[1, 2:5]),
                fig.add_subplot(gs[:, 5]))


    inst = mne.epochs.make_fixed_length_epochs(
            inst,
            duration=2,
            preload=True,
            verbose=False)

    # topo
    mne.viz.ica._plot_ica_topomap(ica, pick, show=False, axes=axs[0], cmap = cmap)

    # specrum
    Nyquist = inst.info['sfreq'] / 2.
    from mne.io.pick import _picks_to_idx
    pick = _picks_to_idx(ica.info, pick, 'all')[0]

    sources = ica.get_sources(inst)
    data = ica.get_sources(inst).get_data()

    psd, freqs = mne.time_frequency.psd.psd_multitaper(sources, fmax = Nyquist, picks=pick)
    psd_ylabel, psds_mean, spectrum_std = mne.viz.ica._get_psd_label_and_std(
            psd, True, ica, 1)
    axs[1].plot(freqs, psds_mean.T, color = "black")
    axs[1].set_xlabel('Frequency (Hz)')
    axs[1].set_ylabel('dB')

    psd, freqs = mne.time_frequency.psd.psd_multitaper(sources, fmax = 70., picks=pick)
    psd_ylabel, psds_mean, spectrum_std = mne.viz.ica._get_psd_label_and_std(
            psd, True, ica, 1)
    axs[2].plot(freqs, psds_mean.T, color = "black")
    axs[2].set_xlabel('Frequency (Hz)')
    axs[2].set_ylabel('dB')

    y_pos = np.arange(len(class_labels))
    axs[3].barh(y_pos, class_percent)
    axs[3].set_yticks(y_pos)
    axs[3].set_yticklabels(class_labels, rotation=45)
    axs[3].invert_yaxis()  # labels read top-to-bottom
    axs[3].set_xlabel('Percent')
    axs[3].set_title('IClabel Classification')

    return fig
        
import matplotlib.pyplot as plt
import matplotlib.offsetbox
from matplotlib.lines import Line2D

