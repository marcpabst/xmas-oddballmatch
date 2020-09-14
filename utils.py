import meegkit
from meegkit.asr import ASR
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

def apply_asr(raw, calibrate_window, picks = "eeg"):


    sfreq = raw.info["sfreq"]
    
    ix = mne.channel_indices_by_type(raw.info, picks)["eeg"]
    data = raw._data[ix,:]

    asr = ASR(method='euclid')
    start_t, end_t = calibrate_window
    train_idx = np.arange(start_t * sfreq, end_t * sfreq, dtype=int)
    _, sample_mask = asr.fit(data[:, train_idx])


    X = sliding_window(data, window=int(sfreq), step=int(sfreq))
    Y = np.zeros_like(X)
    for i in range(X.shape[1]):
        Y[:, i, :] = asr.transform(X[:, i, :])

    #raw = X.reshape(8, -1)  # reshape to (n_chans, n_times)
    clean = Y.reshape(8, -1)

    raw._data[ix,:] = clean

    return raw

def cut_raw_blocks(raw, events, eventinfo, begin_event, end_event):

    begin_event_id = eventinfo[begin_event]
    end_event_id = eventinfo[end_event]

    begin_idx =  np.squeeze(events[np.where(events[:,2] == begin_event_id),0])
    end_idx = np.squeeze(events[np.where(events[:,2] == end_event_id),0])

    if begin_idx[0] > end_idx[0]: end_idx = end_idx[1:]

    raw._data = np.hstack( [raw._data[:, np.arange(b, e) ] for b, e in zip(begin_idx[0:(len(end_idx)-1)], end_idx) ] )

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

    
