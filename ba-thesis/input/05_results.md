# Results

![ERP grand averages (pooled FZ, F3, F4, FC1, and FC2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for A tones (A-A-A-**A**-X, blue dashed lines) and B tones (A-A-A-A-**B**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants (middle of each panel) and the difference of topographic maps averaged over the same interval (right of each panel).](figures/fig_fronto.png){#fig:fronto}

@Fig:fronto displays grand averages of event-related potentials (ERP) at pooled FZ, F3, F4, FC1, and FC2 electrode locations to A tones (A-A-A-**A**-X), B tones (A-A-A-A-**B**), and their difference (**B** tone minus **A** tone) for both 100 ms (left panel) and 150 ms (right panel) SOAs. The top half of each panel shows ERPs in the *predictable condition* while the lower half depicts ERPs in the *random condition*. Clearly visible rhythms result from fast presentation frequencies and illustrate the considerable overlap between neighboring tones. Panels also show the distribution of mean amplitude differences in the MMN latency window across participants and the difference of scalp topographies. Similarly, waveforms and mean amplitude difference distributions at pooled mastoid sites are shown in @fig:mastoids.

![ERP grand averages (pooled M1, M2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for A tones (A-A-A-**A**-X, blue dashed lines) and B tones (A-A-A-A-**B**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants.](figures/fig_mastoids.png){#fig:mastoids}

The MMN latency window was determined to range from 108 ms to 158 ms ofter stimilus onset for 100 ms SOA and from 104 ms to 154 ms after stimulus onset for 150 ms SOA. Mean amplitudes from that interval are shown in Table 1. Descriptively, mean amplitudes at pooled frontocentral electrode locations were more negative for randomly presented B tones than for randomly presented A tones, regardless of presentation rate (100 ms: {{{desc_rand_a_b_100}}}; 150 ms: {{{desc_rand_a_b_150}}}). A simmilar observation could be made for predictable tones presented at 150 ms SOA  ({{{desc_pred_a_b_150}}}), Strikingly hoewever, when presented at 100 ms SOA, B tones seemed to elicit more positive responses than A tones ({{{desc_pred_a_b_100}}}). 

Statistical analysis was carried out using independent two-way repeated-measures analysis of variance (ANOVA, Table 2). For the 100 ms SOA presentation,  ANOVA results for the frontocentral electrode cluster revealed a significant effect of the interaction term (*condition* x *stimulus type*; {{{anova_03_100_fronto_condition_stimulustype}}}). For slower tone presentation ($SOA = 150 ms$ ), ANOVA results suggested a main effect of factor *stimulus type* for both frontocentral ({{{anova_03_150_fronto_stimulustype}}}) and mastoid electrodes ({{{anova_03_150_mastoids_stimulustype}}}). ANOVAs for the comparison between the 4th A tone and the 5th A tone (A-A-A-**A**-X versus A-A-A-A-**A**; Table 2) did not result in any significant effects.


```{=latex}
\input{tables/anova_03_full.tex}
```

Significant interactions indicate that difference waves between A and B tones differ across conditions. Two-tailed Student's *t*-tests and complementary Bayesian analysis were used to test individual MMN responses for significance from zero. P-values were corrected for multiple comparisons using the Benjamini–Hochberg step-up procedure. Results indicate that responses to B tones are more positive in comparisons to A tones when presented in a predictable context ({{{posthoc_pred_a_b_fronto_100}}}). Although descriptive statistics indicated a contrary effect for randomly tones presented, results remained inconclusive ({{{posthoc_rand_a_b_fronto_100}}}).




![Averaged voltages in the MMN latency window for pooled frontocentral and mastoid electrodes. Colored areas show sample probability density function for A tones (green) and B tones (red). White diamonds indicate estimated population mean, vertical bars represent 95%-conficence interval. Only Benjamini-Hochberg-corrected  p-values $< 0.05$ are shown.](figures/fig_posthoc.png)

![ERP grand averages (pooled FZ, F3, F4, FC1, and FC2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for 4th A tones (A-A-A-**A**-X, blue dashed lines) and 5th A tones (A-A-A-A-**A**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants (middle of each panel) and the difference of topographic maps averaged over the same interval (right of each panel).](figures/fig_fronto2.png){#fig:fronto2}
```{=latex}
\input{tables/anova2_03_full.tex}
```

To investigate whether absence of evidence for an MMN might be due to low whin-participant sample sizes, the anaylsis was repeated for the *random* condition including not only B tone trials that occured within a five-tone sequence (as with the pregistrated analyis path), but all B tones and their immediately preceding A tone. Results from this comparison are shown in @Fig:??.

![EEG waveforms for five-tone sequences presented in an predictable context (dotted line) and pseudo-random condition (dashed line) for 100 ms presentation rate (top panel) and 150 ms presentation rate (lower pabel). Vertical lines indicate tone onset.](figures/fig_subsample_rel.png){#fig:rel}

Split-half reliabilities are displayed in @fig:rel. Simulated values match the curve expected from the  Spearman-Brown formula. In the context of classcial test theory, this method relates the length of a test (or *experiment*) to the number of items (or *trials*). The first derivitve of the Spearman-Brown function is monotonically decreasing, leading to two different observation: i) Adding additional epochs (extending the test length by an absolute value in classcial test theory terms) has a large effect when the number of already present epochs is low, but has only little effect when already dealing with large numbers of epochs and ii) SOA and thus effect sized have a larger impact when epoch numbers are small compared to high epoch numbers. Graphed values also show that reliabilities for the 100 ms stimulation rate are considerably lower than for an SOA of 150 ms and that reliabilities are very low when using a relatively small number of epochs. There is no generally accepted rule as to the level above which the coefficient can be considered acceptable. Rather, reliabiliy should be evaluated based on the purpose of a study considering the cost-benefit trade-off [@nunnallyPsychometricTheory1994]. As laid out, inreased realibility comes at overproportionate cost, in that collecting more samples will not increase ralibility by the same factor. That said, many published articles deem reliability coefficients above .7 or .8 "acceptable" [@lanceSourcesFourCommonly2006].



\newpage




