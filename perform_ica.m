function EEG = perform_ica(EEG, csv_path, tmp_path)
%perform_ica - MATLAB helper for applying AMICA
    EEG = eeg_checkset(EEG)
    % load channel locations
    EEG = pop_chanedit(EEG, 'lookup', 'res/standard-10-5-cap385.elp');
    % apply ASR TODO: move to Python 
    EEG = pop_clean_rawdata(EEG,'FlatlineCriterion','off','ChannelCriterion',0.8,'LineNoiseCriterion','off','Highpass','off','BurstCriterion',20,'WindowCriterion',0.25,'BurstRejection', 'on','Distance','Euclidian','WindowCriterionTolerances',[-Inf 7] );
    
    % set arguments for amica
    
    
    
    % run amica
    [W,S,mods] = runamica15(EEG.data(:,:),arglist{:});

    % set values in EEG structure
    EEG.icaweights = W;
    EEG.icasphere = S(1:size(W,1),:);
    EEG.icawinv = mods.A(:,:,1);
    EEG.mods = mods;
    EEG.icachansind = 1:EEG.nbchan;

    % run iclabel
    EEG = iclabel(EEG);

    % save to csv
    table = array2table(EEG.etc.ic_classification.ICLabel.classifications);
    table.Properties.VariableNames(:) = EEG.etc.ic_classification.ICLabel.classes;
    writetable(table, csv_path);
end
