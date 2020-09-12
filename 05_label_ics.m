
load("fddf.mat") 
EEG.chanlocs = [EEG.chanlocs{:}]
[EEG.chanlocs(1:34).Z] = deal([]); 
[EEG.chanlocs(1:34).Y] = deal([]); 
[EEG.chanlocs(1:34).X] = deal([]); 
EEG.pnts = double(EEG.pnts)
EEG.trials = double(EEG.trials)
EEG = pop_chanedit(EEG)
EEG = iclabel(EEG)
pop_viewprops(EEG, 0)