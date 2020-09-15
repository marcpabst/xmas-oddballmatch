function label_ics(input, output)
    % load prepared *.mat file
    input = load(input);
    % fix conversion issue
    input.EEG.chanlocs = [input.EEG.chanlocs{:}];

    % fix type issue
    input.EEG.pnts = double(input.EEG.pnts);
    input.EEG.trials = double(input.EEG.trials);

    input.EEG = pop_chanedit(input.EEG, 'lookup', 'matlab/standard-10-5-cap385.elp');
    % run iclabel
    input.EEG = iclabel(input.EEG);

    table = array2table(input.EEG.etc.ic_classification.ICLabel.classifications);
    table.Properties.VariableNames(:) = input.EEG.etc.ic_classification.ICLabel.classes;
    writetable(table, output);
end