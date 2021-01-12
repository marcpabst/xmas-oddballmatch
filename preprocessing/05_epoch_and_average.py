from parsl.app.app import python_app

@python_app
def epoch_and_average(id, config, inputs=[]):
    import mne
    from autoreject import AutoReject
    import utils
    import sys


    # Read file from disk
    input_pipeline_name = config.get("input_pipeline_name", config["pipeline_name"])
    raw_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, input_pipeline_name, ".fif", suffix="raw", processing="cleaned")
    events_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, input_pipeline_name, ".txt", suffix="eve", processing="prepared")
    raw = mne.io.read_raw_fif(raw_filename, preload=True)
    events = mne.read_events(events_filename)

    # Logging
    log_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".txt", suffix="log")
    sys.stdout = open(log_filename, 'w', buffering = 1)

    # Epoch data
    raw.pick(["eeg", "eog"])
    epochs = mne.Epochs(raw, events, config["events_dict"],
                        tmin=config["epoch_window"][0],
                        tmax=config["epoch_window"][1],
                        baseline=config["baseline_window"],
                        #reject=config["diff_criterion"],
                        reject=None,
                        preload=True)

    raw = raw.set_channel_types(
        {"vEOG": "eog", "hEOG": "eog"})

    if config["use_autoreject"] is not None and config["use_autoreject"]:
        print("Running AutoReject...")
        ar = AutoReject(verbose = False)
        ar.fit(epochs)
        epochs = ar.transform(epochs)
        
    elif config["diff_criterion"] is not None:
        epochs = epochs.drop_bad(config["diff_criterion"])

    evokeds_list = []
    for condition in config["conditions_of_interest"]:
        evoked = epochs[condition].average()
        evoked.comment = condition
        evokeds_list.append(evoked)

    ave_filename = utils.get_derivative_file_name(
        config["bids_root_path"], id, config["pipeline_name"], ".fif", suffix="ave")

    mne.write_evokeds(ave_filename, evokeds_list)
