from autoreject import get_rejection_threshold

def preprocess_ica(raw):
    
    # cut continous data into arbitryt epochs of 1s
    events = mne.make_fixed_length_events(raw, duration=1.0)
    epochs = mne.Epochs(raw, events, tmin=0.0, tmax=tstep)
    reject = get_rejection_threshold(epochs)
    ica.fit(epochs, reject=reject, tstep=tstep)
