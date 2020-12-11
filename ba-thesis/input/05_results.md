\newpage
# Results

![ERP grand averages (pooled FZ, F3, F4, FC1, and FC2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for A tones (A-A-A-**A**-X, blue dashed lines) and B tones (A-A-A-A-**B**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants (middle of each panel) and the difference of topographic maps averaged over the same interval (right of each panel).](figures/fig_fronto.png){#fig:fronto}
![ERP grand averages (pooled FZ, F3, F4, FC1, and FC2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for 4th A tones (A-A-A-**A**-X, blue dashed lines) and 5th A tones (A-A-A-A-**A**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants (middle of each panel) and the difference of topographic maps averaged over the same interval (right of each panel).](figures/fig_fronto2.png){#fig:fronto2}

@Fig:fronto displays grand averages of event-related potentials (ERP) at pooled FZ, F3, F4, FC1, and FC2 electrode locations to A tones (A-A-A-**A**-X), B tones (A-A-A-A-**B**), and their difference (B tone minus A tone) for both 100 ms (left panel) and 150 ms (right panel) SOAs. The top half of each panel shows ERPs in the *predictable condition* while the lower half depicts ERPs in the *random condition*. Clearly visible rhythms result from fast presentation frequencies and illustrate the considerable overlap between neighboring tones. Panels also show the distribution of mean amplitude differences in the MMN latency window across participants and the difference of scalp topographies. Similarly, waveforms and mean amplitude difference distributions at pooled mastoid sites are shown in @fig:mastoids.

![ERP grand averages (pooled M1, M2 electrode locations) for an SOA of 100 ms (left) and 150 ms (right), for A tones (A-A-A-**A**-X, blue dashed lines) and B tones (A-A-A-A-**B**, orange dashed line) and their difference (B - A, green solid line). Upper panels show ERPs for tones presented in a predcitable pattern (*predcitable condition*) while lower panels show ERPs for tones presented in pseudo-random order (*random condition*). Shaded area marks MMN latency window (110 ms to 160 ms) used to calculate the distribution of amplitude differences across particpants.](figures/fig_mastoids.png){#fig:mastoids}
```{=latex}
\input{tables/anova2_03_full.tex}
```

```{=latex}
\input{tables/anova_03_full.tex}
```
![Averaged voltages in the MMN latency window for pooled frontocentral and mastoid electrodes. Colored areas show sample probability density function for A tones (green) and B tones (red). White diamonds indicate estimated population mean, vertical bars represent 95%-conficence interval.](figures/fig_posthoc.png)

#### 100 ms Presentation Rate.
The MMN latency window was determined to range from 108 ms to 158 ms ofter stimilus onset. Descriptively, mean amplitudes at pooled frontocentral electrode locations were more negative for randomly presented B tones than for randomly presented A tones  ({{{desc_rand_a_b_100}}}). Strikingly however, B tones seemed to elicit more positive responses than associated A tones ({{{desc_pred_a_b_100}}}). 

ANOVA results for the frontocentral electrode cluster revealed a significant effect of the interaction term (*condition* x *stimulus type*; {{{anova_03_100_fronto_condition_stimulustype}}}) indicating that difference waves for A and B tones differed between condition. Complemantary analysis for 4th A tones and the 5th A tones (A-A-A-**A**-X versus A-A-A-A-**A**; Table 2) did not result in any significant effects.

Two-tailed Student's *t*-tests and complementary Bayesian analysis were used to test MMN responses at the frontocentral electrode cluster for significance from zero. The Benjamini–Hochberg step-up procedure was employed to correct p-values for multiple comparisons. Results indicated that B tones eclicted more positive responses compared to A tones when presented in a predictable context ({{{posthoc_pred_a_b_fronto_100}}}). Although descriptive statistics suggested a contrary effect for randomly presented tones, results remained inconclusive ({{{posthoc_rand_a_b_fronto_100}}}).

#### 150 ms Presentation Rate.
Calculation of MMN window of interest resulted in an interval from 104 ms to 154 ms after stimulus onset. Descriptivly, B tones in that interval were more negative than corresponding A tones for both *predcitable*  ({{{desc_pred_a_b_150}}}) and *random* condition ({{{desc_rand_a_b_150}}}). ANOVA results suggested a main effect of factor *stimulus type* for both frontocentral ({{{anova_03_150_fronto_stimulustype}}}) and mastoid electrodes ({{{anova_03_150_mastoids_stimulustype}}}). Since no significant interaction effect was present, no follow-up tests were performed.
 


![Average split-half reliabilities for A and B tones in random and predictable contexts.. Negative values might be interpreted as low or no reliability [@cronbachNoteNegativeReliabilities1954]. Thin lines in the 150 ms condition indicate extrapolation using the Spearman-Brown formula.](figures/fig_subsample_rel.png){#fig:rel}

#### Analysing Split-Half-Reliabilities.
Average split-half reliabilities ([@Fig:rel]) demonstrate that reliability can be characterized as a function of epoch number. Whereas a high number of epochs provided reasonable reliability, particularly small samples resulted in highly unreliable estimates. This observation might serve as a plausible explanation for the inconclusive result in the 100 ms condition, as epoch numbers for B tones ($N_{avg} = 364.4$) could be inadequately low to obtain a reliable estimate. In comparison, including all B tones (instead of only tones that were part of a five-tone pattern and akin to @sussmanOrganizationSequentialSounds2005), on average led to an eightfold increase in epoch numbers ($N_{avg} = 2919.8$). Interestingly, statistical comparison for such an extended sample was no longer inconclusive but indicated strong evidence in favor of more negative responses to B tones than to A tones ({{{random_alternative_contrast_100_a_b}}}). 






