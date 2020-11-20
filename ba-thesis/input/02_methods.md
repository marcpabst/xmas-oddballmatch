# Methods
## Data Acquisition

### Participants

#### Study 1

Twenty-three psychology undergraduate students (2 males, average age 22.6 yrs., $SD=5.57$, range 18 - 42 yrs.) were recruited at the Institute of Psychology at the University of Leipzig. All participants reported good general health, normal hearing and had normal or corrected-to-normal vision. Written informed consent was obtained before the experiment. One-third (34.8%) of participants spent time enaging in musical activities at time of survey, while 8.7% had no prior experience in music training. Handedness was asseced using a modified version of the Edinburgh Handedness Inventory [@oldfieldAssessmentAnalysisHandedness1971, see appendix]. A majoritiy (00%) of parcicipants favored the right hand.  Particpants were blinded in respect to the purpose of the experiment and received course credit in compensation.

#### Study 2

Twenty healthy participants (0 males, average age 00.0 yrs., $SD=0.00$, range 00 - 00 yrs.) were recruited. Particpants gave informed consent and reported normal hearing and corrected or corrected-to-normal vision. All participants were naive regarding the purpose of the experiment and were compensated in cource credit or money. 00 participants (00%) had received musical training in the last 5 years before the experiment while 00 (00%) reported no musical experiance. In addition, participants reported if streaming occured during the presentation of the tones.

### Stimuli
![ Tones of two different frequencies (A=440 Hz, B=449 Hz) were presented in two blocked conditions: In the “predictable” condition (top half), tones followed a simple pattern in which a single B-tone followed four A-tones. Some designated B-tones were replaced by A-tones ("pattern deviants"). In the "random" condition (lower half), tones were presented in a pseudo-random fashion ()  ](figures/fig1.png)

Stimuli consisted of pure sinusoidal tones with a duration of 50 ms (including a 10 ms cosine on/off ramp), presented isochronously at a stimulation onsets asynchrony (SOA) of 100 ms for study 1 and 150 ms for study 2. Participants where seated in a electromagnetically shielded and sound-proofed cabin while administering a total of 40 blocks containing a mixture of frequent 440 Hz tones (“A” tones) and infrequent 449 Hz tones ("B" tones). In one half of the blocks, tones were presented in pseudo-random order (e.g. A-A-A-B-A-B-A}, "random" condition), while in the remaining  block tone presentation followed a simple pattern in which a five-tone-sequence of four frequent tones and one infrequent tone (i.e. A-A-A-A-B) was repeated cyclically ("predictable" condition). The ratio of frequent and infrequent tones was 10% for both conditions. Within the predictable condition, 10% of designated (infrequent) B tones were replaced by A tones, resulting in sporadic five-tone sequences consisting solely of A tones (i.e. A-A-A-A-A), thus violating the predictability rule. To assure comparability of local histories between tones in both conditions, randomly arranged tones were interspersed with sequences mimicking aforementioned patterns from the predictable condition (B-A-A-A-A-B and B-A-A-A-A-A) in the random condition. A grand total of 2000 tones in study 1 and 4000 tones in study 2 were delivered to each participant. 

### Data Acquisition

Electrophysiological data was recorded from active silver-silver-chloride (*Ag*-*AgCl*) electrodes using an ActiveTwo amplifier (BioSemi B.V., Amsterdam, The Netherlands). Acquisition was monitored online to ensure optimal data quality. A total of 39 channels were obtained using a 32-electrode-cap and 7 external electrodes. Scalp electrode locations conformed to the international 10–20 system. Horizontal and vertical eye movement was obtained using two bipolar configurations with electrodes placed around the lateral canthi of the eyes and above and below the right eye. Additionally,  electrodes were placed on the tip of the nose and at the left and right mastoid sites. Data was sampled at 512 Hz and on-line filtered at 1000 Hz.


## Analysis Pipeline

Data prepossessing was implemented using a custom pipeline based on the *MNE Python* software package [@gramfortMEGEEGData2013] using *Python 3.7*. All computations were carried out on a cluster operated by the University Computation Center of the University of Leipzig. Code used in thesis is publicly available at <https://github.com/marcpabst/xmas-oddballmatch>. 

### Bad Channel Detection and Interpolation

Firstly, EEG data was subject to the ZapLine procedure [@decheveigneZapLineSimpleEffective2020] to remove line noise contamination. A fivefold detection procedure as described by @bigdely-shamloPREPPipelineStandardized2015 was then used to detect and subsequently interpolate bad channels. This specifically included the detection of channels thain contain prolonged segments with verry small values (i.e. flat channels), the exclusion of channels based on robust standard deviation (deviation criterion), unusualy pronounced high-frequency noise (noisiness criterion), and the removal of channels that were poorly predicted by nearby channels (correlation criterion and predictability criterion). Channels considered bad by one or more of these methods were removed and interpolated using spherical splines [@perrinSphericalSplinesScalp1989]. Electrode locations for interpolations were informed by the BESA Spherical Head Model.

### Independent Component Analysis

Given the $\frac{1}{f}$ power spectral density of EEG data, the estimation independent components (ICs) by independent component analysis (ICA) would be strongly influenced by high-frequency noise that is ususally considere brain-irrelevant [reference]. To mitigate this effect, a 1-Hz-high-pass filter (134th order hamming-windowed FIR) was applied prior to ICA [@winklerInfluenceHighpassFiltering2015]. 

To further reduce artifacts, Artifact Subspace Reconstruction [ASR, @mullenRealtimeNeuroimagingCognitive2015] was used to identify parts of the data with unusual characteristics (bursts) which were subsequently removed. ICA was then carried out using the *Picard* algorithm [@ablinFasterICAOrthogonal2017; @ablinFasterIndependentComponent2018] on PCA-whitened data. To avoid rank-deficiency when extracting components from data with one or more interpolated channels, PCA was also used for dimensionality reduction to obtain full-ranked data.

The EEGLAB [version 2020.0, @delormeEEGLABOpenSource2004] software package and the IClabel plugin [version 1.2.6, @pion-tonachiniICLabelAutomatedElectroencephalographic2019] were used to automatically classify estimated components. Only components clearly classified (i.e. confidence above 50%) as resulting from either eye movement, muscular, or heartbeat activity were zeroed-out in the mixing matrix before inversely transform ICs.

### Filtering

In line with recommendations from @widmannDigitalFilterDesign2015 and @decheveigneFiltersWhenWhy2019, a ORDER finite impulse response (FIR) bandpass filter from 0.1 Hz to 30 Hz was applied in forward direction only (Hamming window with 0.0194 passband ripple and 53 dB stopband attenuation). 

### Epoching and Averaging

Continuous data was epoched into 400 ms long segments around stimulus onsets. This included a 100 ms pre-stimulus interval which was used to perform baseline correction by subtracting its mean amplitude from each epoch. The AutoReject software package [@jasAutorejectAutomatedArtifact2017] was used to reject bad epochs. The AutoReject algorithm uses cross-validations and basyan optimaziation to calculate channel-wise peak-to-peak amplitude thresholds that minimizes the root mean square error (RMSE) between the mean (after removing the trials marked as bad) and the median of the data (including all trials). For epochs where only a small subset of channels exceeded the critical threshold, bad channels were interpolated instead of removing the whole epoch.

## Statistical Analysis

### Standard Repetition Effects

### MMN

The dependent variable for analysing missmatch response was calculated by averaging amplitudes within a time window of ±25 ms around the maximum negativity obtained by subtracting the mean ERP timecourse following the (expected) deviant event from the ERP following the (expected) standard event. To obtain mean amplitudes, ERPs to 4th position A tones (A-A-A-**A**-X, **boldface** indicates the tone of interest) and B tones (A-A-A-A-**B**) were averaged seperatly for both the *random* and the *predictable* *condition*. For the *random condition*, only tones that were part of a sequence mimicking the patterns from the predictable condition were included. 

A three-way analysis of variance for repeated measures with the factors stimulus onset asynchronoy (100 ms vs. 150 ms stimulus onset asynchrony), condition (predictabe vs random presenation) and stimulus type (A tones vs. B tone). 

To further analyse Following the pre-registration, a two-way analysis of variance for repeated measures to test for significant differences of mean amplitudes in the MMN window between standard and deviant tones (stimulus type) depending on the condition (predictable vs. random) was calculated seperatly for both 100 ms and 150 ms presentation. In line with @sussmanOrganizationSequentialSounds2005, FZ, F3, F4, FC1, and FC2 electrode locations were averaged. Greenhouse-Geisser correction for lack of sphericity was applied when appropriate. 

For post-hock comparison, two-tailed Student's t-test were calculated for . P-values were corrected for multiple comparisons by using the Benjamini-Hochberg procedure.

[^1]: This is a sample footnote.




