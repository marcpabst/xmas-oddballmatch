# Results

Figure X shows EEG waveform averages (pooled FZ, F3, F4, FC1, and FC2 electrode locations) for five-tone sequences (A-A-A-A-B) presented in a *predictable* (top panel) and *random* contexts (lower panel). 
![EEG waveforms for five-tone sequences presented in an predictable context (dotted line) and pseudo-random condition (dashed line) for 100 ms presentation rate (top panel) and 150 ms presentation rate (lower pabel). Vertical lines indicate tone onset.](figures/fig_sequences.png)

Grand averages of the fronto-cluster (pooled FZ, F3, F4, FC1, and FC2 electrode locations) of event-related potentials for A tones (A-A-A-**A**-X) and B tones (A-A-A-A-**B**) and their difference (B-ERP - A-ERP) are displayed in Figure X for both 100 ms (left panel) and 150 ms (right panel) stimulus onset asynchrony. The top half of each panel shows ERPs in the *predictable condition* while the lower halfs depicts ERPs in the *random condition*. For both presentation rates, clear rythms matching the presentation frequency of 10 Hz (100 ms) respectivly 6.667 Hz (150 ms) are seen resulting from overlap of neighboring tones. Panels also show the distribution of amplitude differences in the MMN latency window as defined above (110 ms to 160 ms after stimulus onset) across particpants and the difference of topographic maps averaged over the same interval. Simmilarly, waveforms at pooled mastoid sites are shown in Figure X.

![ERP grand averages (pooled FZ, F3, F4, FC1, and FC2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for A tones (A-A-A-**A**-X, blue dashed lines) and B tones (A-A-A-A-**B**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants (middle of each panel) and the difference of topographic maps averaged over the same interval (right of each panel).](figures/fig_fronto.png)

![ERP grand averages (pooled M1, M2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for A tones (A-A-A-**A**-X, blue dashed lines) and B tones (A-A-A-A-**B**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants.](figures/fig_mastoids.png)



Descriptively, regardless of tone presentation rate, evoked responses for fornto-central electrode locations in the MMN latency window were more negative for B tones than for A tones in the random condition (100-ms-SOA: {{desc_rand_a_b_100}}, 150-ms-SOA: {{desc_rand_a_b_150}}) This was also true when tones were presented in a predictable fashion, but only for the slower presentation rate ({{desc_pred_a_b_150}})). In contrast, when predcitable tone patterns were presented at the faster 100-ms-presentation rate, B tones were descriptively more positive than A tones ({{desc_pred_a_b_100}}). 

Descriptice comparison of evoked responses from pooled left and right mostoids revealed that pseudo-randomly presented B tones were more positive in the MMN latency window than A tones (100-ms-SOA: {{desc_rand_a_b_100_mastoids}}, 150-ms-SOA: {{desc_rand_a_b_150_mastoids}}). A simmilar observation could be made for precitable B tones compared to the preceeding A tones at a SOA of 150 ms ({{desc_pred_a_b_150_mastoids}})) but not for the faster presentation rate ({{desc_pred_a_b_100_mastoids}}). Mean amplitudes in the MMN latency window and their standard deviantions (SD) for all conditions are shown in Table X.

```{=latex}
\input{tables/desc_table.tex}
```

Statistical analysis supports these findings. For the 100 ms stimulation rate, the three-way ANOVA yielded a significant 3-way interaction effect condition x stimulus type x electrode ({{anova_02_100_condition_stimulustype_electrode}}) but revelad no main effects for neither stimulus type ({{anova_02_100_stimulustype}}), condition ({{anova_02_100_condition}}), nor electrode ({{anova_02_100_electrode}}). In contrast, for tones presented at a SOA of 150 ms, an effect was only found for the two-way interaction term stimulus type x electrode ({{anova_02_150_stimulustype_electrode}}). Mean amplitudes in the MMN latency window did not differ for factors stimulus type ({{anova_02_150_stimulustype}}), electrode ({{anova_01_150_electrode}) or condition ({{anova_01_150_condition}}).

```{=latex}
\input{tables/anova_02_full.tex}
```

Two-way ANOVAs (*Condition* x *Stimulus Type*) were carried out seperatly for pooled fronto-central and mostoid electrode locations. For 100 ms tone presenation rate,  the Condition x StimulusType interaction only revealed a significant effect for the fronto-central electrode cluster  ({{anova_03_100_fronto_condition_stimulustype}}) but not for pooled mastoid sites  ({{anova_03_100_mastoids_condition_stimulustype}}) indicating that the 3-way interaction effect condition x stimulus type x electrode is indeed driven by the amplitude differnces in te fronto-central electrode locations . Contrary to this, for the 150 ms presentation rate, main effects for *stimulus type* were significant for both fronto-central and mastoid sites, suggesting that there was both a MMN at fronto-central locations as well as a polarity-reversal at the mastoid electrodes.

```{=latex}
\input{tables/anova_03_full.tex}
```

For the 150 ms stimulation rate, the 2-way ANOVA yielded a significant main effect for stimulus type ({{anova_01_150_stimulustype}}) but not for condition ({{anova_01_150_condition}}) or  stimulus type x condition interaction ({{anova_01_150_condition_stimulustype}}). In contrast, when presenting tones with a stimulus-onset-assychrnony of 100 ms, no such effects were found for the factor condition ({{anova_01_150_condition}}), stimulus type ({{anova_01_150_stimulustype}}), or interaction ({{anova_01_150_condition_stimulustype}}).





