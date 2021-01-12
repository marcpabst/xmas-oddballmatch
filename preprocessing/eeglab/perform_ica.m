function EEG = perform_ica(EEG, csv_path, tmp_path)
%perform_ica - MATLAB helper for applying AMICA
    EEG = eeg_checkset(EEG)
    % load channel locations
    EEG = pop_chanedit(EEG, 'lookup', 'standard-10-5-cap385.elp');
    % apply ASR TODO: move to Python 
    EEG = pop_clean_rawdata(EEG, 'FlatlineCriterion',5,'ChannelCriterion',0.8,'LineNoiseCriterion',4,'Highpass','off','BurstCriterion',20,'WindowCriterion',0.25,'BurstRejection','on','Distance','Euclidian','WindowCriterionTolerances',[-Inf 7] );

    % set arguments for amica
    %arglist = {'outdir', strcat(tmp_path, '/amicaout'), 'num_chans', EEG.nbchan, 'pcakeep', EEG.nbchan, 'max_threads', 4};
    
    % run amica
    %[W,S,mods] = runamica15(EEG.data(:,:),arglist{:});

    % set values in EEG structure
    %EEG.icaweights = W;
    %EEG.icasphere = S(1:size(W,1),:);
    %EEG.icawinv = mods.A(:,:,1);
    %EEG.mods = mods;
    %EEG.icachansind = 1:EEG.nbchan;

    EEG = pop_runica(EEG, 'icatype', 'runica', 'extended',1);

    % run iclabel
    EEG = iclabel(EEG);

    % save to csv
    table = array2table(EEG.etc.ic_classification.ICLabel.classifications);
    table.Properties.VariableNames(:) = EEG.etc.ic_classification.ICLabel.classes;
    writetable(table, csv_path);
end
