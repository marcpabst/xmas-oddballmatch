import meegkit
from meegkit.asr import ASR, clean_windows
from meegkit.utils.matrix import sliding_window
import numpy as np

from mne_bids import make_bids_basename, read_raw_bids, write_raw_bids

from os.path import join, exists
from os import makedirs

import mne

def apply_zapline(raw, fline, picks = "eeg", nremove=1):
    sfreq = raw.info["sfreq"]
    ix = mne.channel_indices_by_type(raw.info, picks)["eeg"]
    data = np.transpose(raw._data[ix,:])
   # data = np.expand_dims(data, 2)

    denoised_data, artifacts = meegkit.dss.dss_line(data, fline, sfreq, nremove=nremove)

    raw._data[ix,:] = np.transpose(denoised_data)

    return raw

def asr(X, sfreq, ref_maxbadchannels = 0.075, ref_tolerances = [-3.5, 5.5], ref_wndlen = 1):

    asr = ASR(method='euclid', sfreq = sfreq)

    nchan = X.shape[0]

    print(X.shape, nchan)

    data = X * 1000000

    asr.fit(data)
    print("ASR calibrated.")
  

    # Apply filter using sliding (non-overlapping) windows
    X = sliding_window(data, window=int(sfreq), step=int(sfreq))
    Y = np.zeros_like(X)
    for i in range(X.shape[1]):
        Y[:, i, :] = asr.transform(X[:, i, :])

    #raw = X.reshape(nchan, -1)  # reshape to (n_chans, n_times)
    clean = Y.reshape(nchan, -1)

    print(clean.shape)
    print("ASR finished. Now comparing signals...")

    sample_mask = np.sum(np.abs(data - clean), 0) < 1e-10

    # find latency of regions
    retain_data_intervals = np.reshape( np.argwhere(np.diff([False] + sample_mask + [False])), 2,[])
    retain_data_intervals[:,1] = retain_data_intervals[:,1]-1

    # reject regions
    new_data = data[:, retain_data_intervals]

    return new_data / 1000000

def cut_raw_blocks(raw, events, eventinfo, begin_event, end_event):
    sfreq = raw.info["sfreq"]

    begin_event_id = eventinfo[begin_event]
    end_event_id = eventinfo[end_event]

    begin_idx =  np.squeeze(events [np.where(events[:,2] == end_event_id), 0] )
    end_idx = np.squeeze(events[np.where(events[:,2] == begin_event_id), 0])

    if begin_idx[0] > end_idx[0]:
        end_idx = end_idx[1:]

    if len(begin_idx) is not len(end_idx):
        min_len = min([len(begin_idx), len(end_idx)])
        begin_idx = begin_idx[0:min_len]
        end_idx = end_idx[0:min_len]

    print(*["Annotating from {b} s to {e} s.".format(b=b/ sfreq,e=e/ sfreq) for b,e in zip(begin_idx, end_idx)])

    annot = mne.Annotations(begin_idx / sfreq, (end_idx - begin_idx) / sfreq, "bad_nonblock")
    raw.set_annotations(annot)

    return raw

def get_derivative_file_name(bids_root_path, subject, pipeline_name, extension="", make_dir = True, **kwargs):

    derivivite_root_path = join(bids_root_path, "derivatives", pipeline_name) 
    save_dir = join(derivivite_root_path, "sub-"+subject)
    bids_basename = make_bids_basename(subject=subject, **kwargs)

    if make_dir and not exists(save_dir):
        makedirs(save_dir)

    return join(save_dir, bids_basename) + extension

def get_derivative_report_file_name(bids_root_path, subject, pipeline_name, extension=".html", make_dir = True, **kwargs):

    derivivite_root_path = join(bids_root_path, "derivatives", pipeline_name) 
    save_dir = join(derivivite_root_path)
    bids_basename = make_bids_basename(subject=subject, **kwargs)

    if make_dir and not exists(save_dir):
        makedirs(save_dir)

    return join(save_dir, bids_basename) + extension

    
def get_mean_amplitudes(evokeds, window, picks = "all"):

    means = []
    if isinstance(evokeds, list):
        for i, evoked in enumerate(evokeds):
            evoked = evoked.copy().pick(picks)

            _window = np.arange(evoked.time_as_index(window[0]),
                                evoked.time_as_index(window[1]))

            data = evoked.data[:, _window]
            mean = data.mean()
            means.append(mean)
    else:
        return get_mean_amplitudes([evokeds], window, picks)

    return means


def write_set(fname, raw):
    """Export raw to EEGLAB .set file."""
    import numpy as np
    from numpy.core.records import fromarrays
    from scipy.io import savemat
    data = raw.get_data() * 1e6  # convert to microvolts
    fs = raw.info["sfreq"]
    times = raw.times
    ch_names = raw.info["ch_names"]
    chanlocs = fromarrays([ch_names], names=["labels"])
    events = fromarrays([raw.annotations.description,
                         raw.annotations.onset * fs + 1,
                         raw.annotations.duration * fs],
                        names=["type", "latency", "duration"])
    savemat(fname, dict(EEG=dict(data=data,
                                 setname=fname,
                                 nbchan=data.shape[0],
                                 pnts=data.shape[1],
                                 trials=1,
                                 srate=fs,
                                 xmin=times[0],
                                 xmax=times[-1],
                                 chanlocs=chanlocs,
                                 event=events,
                                 icawinv=[],
                                 icasphere=[],
                                 icaweights=[])),
            appendmat=False)
