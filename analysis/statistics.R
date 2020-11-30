library(tidyverse)
library(lme4)
library(lmerTest)
library(ggpubr)
library(rstatix)
library(xtable)
library(huxtable)
library(stringr)
library(lemon)
library(ggthemes)
library(Cairo)

source("plot_functions.R")

### LOAD DATA ###
tables_path = "/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/tables"

mean_amplitudes_df = readr::read_csv("../data/mean_amplitudes.csv")
mean_amplitudes_df = mean_amplitudes_df %>% mutate(Participant = factor(Participant), SOA = factor(SOA), Electrode = factor(Electrode), Condition = factor(Condition), StimulusType = factor(StimulusType))

n1_mean_amplitudes_df = readr::read_csv("../data/n1_mean_amplitudes.csv")
n1_mean_amplitudes_df = n1_mean_amplitudes_df %>% mutate(Participant = factor(Participant), SOA = factor(SOA), Electrode = factor(Electrode), Condition = factor(Condition), StimulusType = factor(StimulusType))
n1_mean_amplitudes_df

variables = list()


batheme <- theme_tufte(base_family = "DejaVu Sans") +
    # remove axis lines
    theme(
        axis.line = element_blank()) +
    # remove legend title
    theme(legend.text  = element_text(size=6),
        legend.title = element_blank()) +
    # set text size
    theme(
        plot.title   = element_text(size=6),
        axis.text.x  = element_text(size=6),
        axis.text.y  = element_text(size=6),
        axis.title.x = element_text(size=6),
        axis.title.y = element_text(size=6)) +
    theme(
        strip.text.x = element_text(size=6, face = "bold"),
        strip.text.y = element_text(size=6, face = "bold")) +
    theme(
        axis.ticks = element_line(size = .35)) +
    theme(
        legend.margin=margin(t = -.15, unit='in'))


# %%



# # %%
# sta_data_150 = n1_mean_amplitudes_df %>% filter(SOA == "150" & Electrode == "fronto_pooled" & StimulusType != "B-5" & StimulusType != "A-5") %>% 
#             mutate(StimulusType = as.integer( substr(StimulusType, 3, 3) )) %>% droplevels()

# model1 = lmer(MeanAmplitude ~ Condition +  (1 | Participant), data=sta_data_150, REML=FALSE) 
# model2 = lmer(MeanAmplitude ~ Condition + StimulusType + Condition * StimulusType + (1 | Participant), data = sta_data_150, REML=FALSE)


# model3 = lmer(MeanAmplitude ~ StimulusType +  (1 | Participant), data=sta_data_150, REML=FALSE) 
# model4 = lmer(MeanAmplitude ~ Condition + StimulusType + Condition * StimulusType + (1 | Participant), data = sta_data_150, REML=FALSE)


# anova(model1, model2)

# anova(model2)


# # %%
# xtable(anova_04_150_table)


# # %%




### FORMATTING ###

plot_with = 6.25

report_anova = function(test_row) {
    anova_template = "$F(%i,%i) = %.2f$, $%s$"
    return( sprintf(anova_template, 
                test_row %>% pull(DFn),
                test_row %>% pull(DFd),
                test_row %>% pull(F),
                test_row %>% pull(p) %>% fm_pvalue_full() # already formatted
                ))
}


anova_template = "$F(%.0f,%.0f) = %.2f$, $p = %.4f$"

report_ttest = function(test_row) {
    ttest_template = "$t(%i) = %.2f$, $%s$, $CI_{.95} = [%.2f,%.2f]$"
    return( sprintf(ttest_template, 
                test_row %>% pull(df),
                test_row %>% pull(statistic),
                test_row %>% pull(p.adj), # already formatted
                test_row %>% pull(conf.low),
                test_row %>% pull(conf.high)
                ))
}


fm_pvalue = function(p) {
    out = ifelse(p < .001, "< .001", sprintf("%.3f",p))
    out = stringr::str_replace(out, fixed("0."), ".")
    return(out)
}

fm_bf10_full = function(bf) {
    out = sprintf("BF = %.3f", bf)
    return(out)
}

fm_pvalue_full = function(p) {
    out = ifelse(p < .001, "p < .001", sprintf("p = %.3f",p))
    out = stringr::str_replace(out, fixed("0."), ".")
    return(out)
}


### DESCRIBE DATA ###

# Description Tables
desc_table = mean_amplitudes_df %>% filter(Electrode == "fronto_pooled") %>% droplevels() %>%
    group_by(SOA, Condition, StimulusType) %>%
    summarise(Mean = mean(MeanAmplitude)*10e5, SD = sd(MeanAmplitude)*10e5) %>%
    hux() %>%
    merge_repeated_rows(col=c(1,2)) %>%
    theme_article()

desc_table_mastoids = mean_amplitudes_df %>% filter(Electrode == "mastoids_pooled") %>% droplevels() %>%
    group_by(SOA, Condition, StimulusType) %>%
    summarise(Mean = mean(MeanAmplitude)*10e5, SD = sd(MeanAmplitude)*10e5) %>% ungroup() %>%
    select(Mean, SD) %>%
    hux() %>%
    merge_repeated_rows(col=c(1,2)) %>%
    theme_article()

desc_table_final = cbind(desc_table,desc_table_mastoids) %>%
    set_caption("Means and standard deviations for condition, stimulus type and electrodes.")

write(to_latex(desc_table_final), paste(tables_path, "desc_table.tex", sep="/"))

# Description Deltas

desc_table_intern1 = mean_amplitudes_df %>% filter(Electrode == "fronto_pooled") %>% droplevels() %>%
    group_by(SOA, Condition, StimulusType) %>%
    summarise(Mean = mean(MeanAmplitude)*10e5, SD = sd(MeanAmplitude)*10e5)  %>% ungroup() %>%
    group_by(SOA, Condition) %>%
    summarise(delta_mean = Mean[[2]] - Mean[[1]])  %>% ungroup()

delta_mean_template = "$\\Delta M = %.3f \\: \\mu V$"
variables$desc_pred_a_b_100 = sprintf(delta_mean_template, desc_table_intern1 %>% filter(SOA==100 & Condition=="predictable") %>% pull(delta_mean))
variables$desc_rand_a_b_100 = sprintf(delta_mean_template, desc_table_intern1 %>% filter(SOA==100 & Condition=="random") %>% pull(delta_mean))
variables$desc_pred_a_b_150 = sprintf(delta_mean_template, desc_table_intern1 %>% filter(SOA==150 & Condition=="predictable") %>% pull(delta_mean))
variables$desc_rand_a_b_150 = sprintf(delta_mean_template, desc_table_intern1 %>% filter(SOA==150 & Condition=="random") %>% pull(delta_mean))

desc_table_intern2 = mean_amplitudes_df %>% filter(Electrode == "mastoids_pooled") %>% droplevels() %>%
    group_by(SOA, Condition, StimulusType) %>%
    summarise(Mean = mean(MeanAmplitude)*10e5, SD = sd(MeanAmplitude)*10e5)  %>% ungroup() %>%
    group_by(SOA, Condition) %>%
    summarise(delta_mean = Mean[[2]] - Mean[[1]])  %>% ungroup()

variables$desc_pred_a_b_100_mastoids = sprintf(delta_mean_template, desc_table_intern2 %>% filter(SOA==100 & Condition=="predictable") %>% pull(delta_mean))
variables$desc_rand_a_b_100_mastoids = sprintf(delta_mean_template, desc_table_intern2 %>% filter(SOA==100 & Condition=="random") %>% pull(delta_mean))
variables$desc_pred_a_b_150_mastoids = sprintf(delta_mean_template, desc_table_intern2 %>% filter(SOA==150 & Condition=="predictable") %>% pull(delta_mean))
variables$desc_rand_a_b_150_mastoids = sprintf(delta_mean_template, desc_table_intern2 %>% filter(SOA==150 & Condition=="random") %>% pull(delta_mean))


### ANOVAS ###

### standards ###
n1_mean_amplitudes_df %>% mutate(MeanAmplitude = MeanAmplitude*10e5) %>% filter(Electrode == "fronto_pooled") %>% filter(StimulusType != "B-5") %>%
    anova_test(dv = MeanAmplitude,  wid = Participant, between=c(SOA), within = c(Condition, StimulusType)) %>%
                        get_anova_table()

# n1_mean_amplitudes_df %>% mutate(MeanAmplitude = MeanAmplitude*10e5) %>% filter(Electrode == "fronto_pooled") %>% filter(StimulusType != "B-5") %>%
#     ggplot(aes(y = MeanAmplitude, x = StimulusType)) + 
#     facet_rep_grid(rows = vars(SOA), repeat.tick.labels = TRUE) +
#     #geom_boxplot() +
#     #geom_violin(aes(fill=Condition)) +
#     geom_split_violin(aes(fill=Condition), bw = .75, width=.5, key_glyph = draw_key_dotplot, trim=T, grpm = 5) +
#     #geom_point(aes(group= StimulusType), position= position_dodge(.25)) +
#     stat_summary(aes(group= Condition), fun.data = mean_ci, geom = "linerange", position= position_dodge(.25)) +
#     stat_summary(aes(group= Condition), color = "black", fill ="white", fun=mean, geom="point", shape=23, size=1.2, position= position_dodge(.25)) +
#     #stat_summary(color = "black", fun=mean, geom="path", size=.2) +
#     #geom_flat_violin(aes(fill=StimulusType, group=StimulusType), position= position_nudge(0)) +
#     batheme  +
#     xlab("") +
#     ylab("µV") +
#     #scale_y_continuous(limits= c(-5,5),breaks=c(-2.5, 2.5)) +
#     #stat_pvalue_manual(posthoc_tests, hide.ns = T, label = "{p.adj}", label.size = 2, tip.length = 0.01, linetype = "blank") +
#     #scale_x_discrete(expand = c(.2, .2)) +
#     theme(legend.position = "none") +
#     theme(legend.position="bottom") +
#     guides(fill=guide_legend(
#                  keywidth=0.2,
#                  keyheight=0.2,
#                  default.unit="inch")
#       )

### 100 ms ###

## ANOVA for 100 ms with pooled electrodes (fronto x mastoids x stimulus type)
anova_02_100_data = mean_amplitudes_df %>% filter(SOA == "100") %>% filter(Electrode == "fronto_pooled" | Electrode == "mastoids_pooled") %>% droplevels() %>% mutate(MeanAmplitude = MeanAmplitude*10e5)

anova_02_100_table =    anova_02_100_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType, Electrode)) %>%
                        get_anova_table(correction = "auto")
anova_02_100_table$Effect = str_replace_all(anova_02_100_table$Effect, ":", " x ")
class(anova_02_100_table) = "data.frame"

variables$anova_02_100_condition = anova_02_100_table %>% filter(Effect == "Condition") %>% report_anova()
variables$anova_02_100_stimulustype = anova_02_100_table %>% filter(Effect == "StimulusType") %>% report_anova()
variables$anova_02_100_electrode = anova_02_100_table %>% filter(Effect == "Electrode") %>% report_anova()
variables$anova_02_100_condition_stimulustype = anova_02_100_table %>% filter(Effect == "Condition x StimulusType") %>% report_anova()
variables$anova_02_100_condition_electrode = anova_02_100_table %>% filter(Effect == "Condition x Electrode") %>% report_anova()
variables$anova_02_100_stimulustype_electrode = anova_02_100_table %>% filter(Effect == "StimulusType x Electrode") %>% report_anova()
variables$anova_02_100_condition_stimulustype_electrode = anova_02_100_table %>% filter(Effect == "Condition x StimulusType x Electrode") %>% report_anova()
print(xtable(anova_02_100_table), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova_01_100.tex", sep="/"))


### 100 ms
## ANOVA for 100 ms with pooled electrodes
anova_01_100_data = mean_amplitudes_df %>% filter(SOA == "100" & Electrode == "fronto_pooled") %>% droplevels() 
anova_01_100_table =    anova_01_100_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                        get_anova_table()
anova_01_100_table$Effect = str_replace_all(anova_01_100_table$Effect, ":", " x ")
variables$anova_01_100_condition = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_100_table$DFn[[1]], anova_01_100_table$DFd[[1]], anova_01_100_table$F[[1]], anova_01_100_table$p[[1]])
variables$anova_01_100_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_100_table$DFn[[2]], anova_01_100_table$DFd[[2]], anova_01_100_table$F[[2]], anova_01_100_table$p[[2]])
variables$anova_01_100_condition_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_100_table$DFn[[3]], anova_01_100_table$DFd[[3]], anova_01_100_table$F[[3]], anova_01_100_table$p[[3]])
caption  = "Results of the 3-way ANOVA (condition x stimulus x electrode) for repeated measures conducted on the mean ERP-amplitudes (time window 111 - 161 ms) at electrode Fz (upper section). The significant interaction between the three factors included was further analyzed by 2-way ANOVAS (stimulus x electrode) conducted separately for the random condition (middle section) and the predictable condition (lower section)."
print(xtable(anova_01_100_table, correction = "auto", caption = caption), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova_02_100.tex", sep="/"))

## ANOVA for 100 ms for fronto
anova_03_100_data = mean_amplitudes_df %>% filter(SOA == "100" & Electrode == "fronto_pooled") %>% droplevels() 
anova_03_100_table = anova_03_100_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova_03_100_table$Effect = str_replace_all(anova_03_100_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 100 ms (only fronto)"
print(xtable(anova_03_100_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova_03_100.tex", sep="/"))

variables$anova_03_100_fronto_condition = sprintf(anova_template, anova_03_100_table$DFn[[1]], anova_03_100_table$DFd[[1]], anova_03_100_table$F[[1]], anova_03_100_table$p[[1]])
variables$anova_03_100_fronto_stimulustype = sprintf(anova_template, anova_03_100_table$DFn[[2]], anova_03_100_table$DFd[[2]], anova_03_100_table$F[[2]], anova_03_100_table$p[[2]])
variables$anova_03_100_fronto_condition_stimulustype = sprintf(anova_template, anova_03_100_table$DFn[[3]], anova_03_100_table$DFd[[3]], anova_03_100_table$F[[3]], anova_03_100_table$p[[3]])

## ANOVA for 100 ms for mastioid
anova_04_100_data =  mean_amplitudes_df %>% filter(SOA == "100" & Electrode == "mastoids_pooled") %>% droplevels() 
anova_04_100_table = anova_04_100_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova_04_100_table$Effect = str_replace_all(anova_04_100_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 100 ms with non-pooled electrodes"
print(xtable(anova_04_100_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova_04_100.tex", sep="/"))

variables$anova_03_100_mastoids_condition = sprintf(anova_template, anova_04_100_table$DFn[[1]], anova_04_100_table$DFd[[1]], anova_04_100_table$F[[1]], anova_04_100_table$p[[1]])
variables$anova_03_100_mastoids_stimulustype = sprintf(anova_template, anova_04_100_table$DFn[[2]], anova_04_100_table$DFd[[2]], anova_04_100_table$F[[2]], anova_04_100_table$p[[2]])
variables$anova_03_100_mastoids_condition_stimulustype = sprintf(anova_template, anova_04_100_table$DFn[[3]], anova_04_100_table$DFd[[3]], anova_04_100_table$F[[3]], anova_04_100_table$p[[3]])

### 150 ms
## ANOVA for 150 ms with pooled electrodes (fronto x mastoids)
anova_02_150_data = mean_amplitudes_df %>% filter(SOA == "150" & (Electrode == "fronto_pooled" | Electrode == "mastoids_pooled")) %>% droplevels()  %>% mutate(MeanAmplitude = MeanAmplitude*10e5) 

anova_02_150_table =    anova_02_150_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType, Electrode)) %>%
                        get_anova_table(correction = "auto")
anova_02_150_table$Effect = str_replace_all(anova_02_150_table$Effect, ":", " x ")
variables$anova_02_150_condition = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_02_150_table$DFn[[1]], anova_02_150_table$DFd[[1]], anova_02_150_table$F[[1]], anova_02_150_table$p[[1]])
variables$anova_02_150_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_02_150_table$DFn[[2]], anova_02_150_table$DFd[[2]], anova_02_150_table$F[[2]], anova_02_150_table$p[[2]])
variables$anova_02_150_electrode = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_02_150_table$DFn[[3]], anova_02_150_table$DFd[[3]], anova_02_150_table$F[[3]], anova_02_150_table$p[[3]])
variables$anova_02_150_condition_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_02_150_table$DFn[[4]], anova_02_150_table$DFd[[4]], anova_02_150_table$F[[4]], anova_02_150_table$p[[4]])
variables$anova_02_150_condition_electrode = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_02_150_table$DFn[[5]], anova_02_150_table$DFd[[5]], anova_02_150_table$F[[5]], anova_02_150_table$p[[5]])
variables$anova_02_150_stimulustype_electrode = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_02_150_table$DFn[[6]], anova_02_150_table$DFd[[6]], anova_02_150_table$F[[6]], anova_02_150_table$p[[6]])
variables$anova_02_150_condition_stimulustype_electrode = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_02_150_table$DFn[[7]], anova_02_150_table$DFd[[7]], anova_02_150_table$F[[7]], anova_02_150_table$p[[7]])
print(xtable(anova_02_150_table), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova_01_150.tex", sep="/"))


## ANOVA for 150 ms with pooled electrodes
anova_01_150_data = mean_amplitudes_df %>% filter(SOA == "150" & Electrode == "fronto_pooled") %>% droplevels() 
anova_01_150_table =    anova_01_150_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                        get_anova_table()
anova_01_150_table$Effect = str_replace_all(anova_01_150_table$Effect, ":", " x ")
variables$anova_01_150_condition = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_150_table$DFn[[1]], anova_01_150_table$DFd[[1]], anova_01_150_table$F[[1]], anova_01_150_table$p[[1]])
variables$anova_01_150_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_150_table$DFn[[2]], anova_01_150_table$DFd[[2]], anova_01_150_table$F[[2]], anova_01_150_table$p[[2]])
variables$anova_01_150_condition_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_150_table$DFn[[3]], anova_01_150_table$DFd[[3]], anova_01_150_table$F[[3]], anova_01_150_table$p[[3]])
print(xtable(anova_01_150_table, correction = "auto"), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova_01_150.tex", sep="/"))



## ANOVA for 150 ms for fronto
anova_03_150_data = mean_amplitudes_df %>% filter(SOA == "150" & Electrode == "fronto_pooled") %>% droplevels() 
anova_03_150_table = anova_03_150_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova_03_150_table$Effect = str_replace_all(anova_03_150_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 150 ms (only fronto)."
print(xtable(anova_03_150_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova_03_150.tex", sep="/"))

variables$anova_03_150_fronto_condition = sprintf(anova_template, anova_03_150_table$DFn[[1]], anova_03_150_table$DFd[[1]], anova_03_150_table$F[[1]], anova_03_150_table$p[[1]])
variables$anova_03_150_fronto_stimulustype = sprintf(anova_template, anova_03_150_table$DFn[[2]], anova_03_150_table$DFd[[2]], anova_03_150_table$F[[2]], anova_03_150_table$p[[2]])
variables$anova_03_150_fronto_condition_stimulustype = sprintf(anova_template, anova_03_150_table$DFn[[3]], anova_03_150_table$DFd[[3]], anova_03_150_table$F[[3]], anova_03_150_table$p[[3]])

## ANOVA for 150 ms for mastioid
anova_04_150_data =  mean_amplitudes_df %>% filter(SOA == "150" & Electrode == "mastoids_pooled") %>% droplevels() 
anova_04_150_table = anova_04_150_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova_04_150_table$Effect = str_replace_all(anova_04_150_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 150 ms (only mastioids)."
print(xtable(anova_04_150_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova_04_150.tex", sep="/"))

variables$anova_03_150_mastoids_condition = sprintf(anova_template, anova_04_150_table$DFn[[1]], anova_04_150_table$DFd[[1]], anova_04_150_table$F[[1]], anova_04_150_table$p[[1]])
variables$anova_03_150_mastoids_stimulustype = sprintf(anova_template, anova_04_150_table$DFn[[2]], anova_04_150_table$DFd[[2]], anova_04_150_table$F[[2]], anova_04_150_table$p[[2]])
variables$anova_03_150_mastoids_condition_stimulustype = sprintf(anova_template, anova_04_150_table$DFn[[3]], anova_04_150_table$DFd[[3]], anova_04_150_table$F[[3]], anova_04_150_table$p[[3]])


## Create more complex tables

anova_02_full_caption  = "Results of the 3-way ANOVA (condition x stimulus x electrode) for repeated measures conducted on the mean ERP-amplitudes (time window 111 - 161 ms) at electrode Fz (upper section). The significant interaction between the three factors included was further analyzed by 2-way ANOVAS (stimulus x electrode) conducted separately for the random condition (middle section) and the predictable condition (lower section)."

anova_02_full_table = rbind(anova_02_100_table %>% add_column(SOA = paste("100", "ms"), .before = 1), anova_02_150_table %>% add_column(SOA = paste("150", "ms"), .before =1)) %>%
                        hux() %>%
                        merge_repeated_rows(col=1) %>%
                        set_rotation(col=1, value=90) %>%
                        set_valign(col=1, value="middle") %>%
                        set_header_rows(1, TRUE) %>%
                        set_contents(1,1, value = "") %>%

                        set_caption(anova_02_full_caption) %>%

                        set_bottom_padding(row=8, value=8) %>%
                        set_top_padding(row=9, value=8) %>%

                        set_bottom_padding(row=8, value=15) %>%
                        set_top_padding(row=9, value=15) %>%
                        theme_article()


write(to_latex(anova_02_full_table), paste(tables_path, "anova_02_full.tex", sep="/"))



############

anova_03_full_caption  = "Results of the 2-way ANOVA (condition x stimulus type) for repeated measures. Only fronto included."


anova_03_full_table_1 = rbind(anova_03_100_table %>% add_column(Electrodes = "Frontal", .before = 1), anova_04_100_table %>% add_column(Electrodes = "Mastoids", .before =1)) 
anova_03_full_table_2 = rbind(anova_03_150_table %>% add_column(Electrodes = "Frontal", .before = 1), anova_04_150_table %>% add_column(Electrodes = "Mastoids", .before =1)) 

anova_03_full_table = rbind(anova_03_full_table_1 %>% add_column(SOA = "100 ms", .before = 1), anova_03_full_table_2 %>% add_column(SOA = "150 ms", .before =1)) %>%  hux() %>%
                        set_number_format(col=7, value=list(fm_pvalue)) %>%
                        merge_repeated_rows(col=c(1,2)) %>%
                        set_rotation(col=c(1,2), value=90) %>%
                        set_valign(col=c(1,2), value="middle") %>%
                        set_header_rows(1, TRUE) %>%
                        set_contents(1,1, value = "") %>%
                        set_contents(1,2, value = "") %>%

                        set_caption(anova_02_full_caption) %>%

                        set_bottom_padding(row=4, value=8) %>%

                        set_top_padding(row=5, value=8) %>%
                        set_bottom_padding(row=7, value=15) %>%

                        set_top_padding(row=8, value=15) %>%
                        set_bottom_padding(row=10, value=8) %>%

                        set_top_padding(row=11, value=8) %>%

                        #set_bottom_padding(row=8, value=15) %>%
                        #set_top_padding(row=9, value=15) %>%
                        theme_article()


write(to_latex(anova_03_full_table), paste(tables_path, "anova_03_full.tex", sep="/"))


### POST-HOC TESTS ###

data = mean_amplitudes_df %>% filter(Electrode == "fronto_pooled" | Electrode == "mastoids_pooled") %>% droplevels() %>% 
    mutate(MeanAmplitude = MeanAmplitude*10e5) %>%
    mutate(SOA = fct_relabel(SOA, ~ paste(., "ms"))) %>%
    mutate(StimulusType = fct_relabel(StimulusType, ~ paste(., "tone"))) %>% 
    mutate(Electrode = fct_recode(Electrode, "Fronto-Central" = "fronto_pooled", "Mastoids" = "mastoids_pooled" )) 

posthoc_tests = data %>%
  group_by(SOA, Condition, Electrode) %>%
  bayesian_t_test(data =., MeanAmplitude ~ StimulusType, paired=T, detailed=T) %>% # verry hacky !
  rename(bf = statistic)
  
posthoc_tests = data %>% 
  group_by(SOA, Condition, Electrode) %>%
  t_test(data =., MeanAmplitude ~ StimulusType, paired=T, detailed=T) %>%
  left_join(posthoc_tests, by = c("SOA", "Condition", "Electrode", "group1", "group2"))  %>%
  adjust_pvalue(method = "fdr") %>%
  add_significance("p.adj") %>%
  add_xy_position(x = "Electrode") %>%
  mutate(p_full = fm_pvalue_full(p.adj)) %>%
  mutate(bf_full = fm_bf10_full(bf)) %>%
  mutate(y.position = 7.5) 



variables$posthoc_pred_a_b_fronto_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "predictable" & Electrode == "Fronto-Central"))
variables$posthoc_pred_a_b_mast_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "predictable" & Electrode == "Mastoids"))

variables$posthoc_rand_a_b_fronto_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "random" & Electrode == "Fronto-Central"))
variables$posthoc_rand_a_b_mast_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "random" & Electrode == "Mastoids"))

variables$posthoc_pred_a_b_fronto_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "predictable" & Electrode == "Fronto-Central"))
variables$posthoc_pred_a_b_mast_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "predictable" & Electrode == "Mastoids"))

variables$posthoc_rand_a_b_fronto_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "random" & Electrode == "Fronto-Central"))
variables$posthoc_rand_a_b_mast_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "random" & Electrode == "Mastoids"))

library(extrafont)


plot_posthoc = ggplot(aes(y = MeanAmplitude, x = Electrode), data = data) + 
    facet_rep_grid(cols = vars(SOA), rows = vars(Condition), repeat.tick.labels = TRUE) +
    #geom_boxplot() +
    geom_split_violin(aes(fill=StimulusType), bw = .75, width=.5, key_glyph = draw_key_dotplot, trim=T) +
    #geom_point(aes(group= StimulusType), position= position_dodge(.25)) +
    stat_summary(aes(group= StimulusType), fun.data = mean_sd, geom = "linerange", position= position_dodge(.25)) +
    stat_summary(aes(group= StimulusType), color = "black", fill ="white", fun=mean, geom="point", shape=23, size=1.2, position= position_dodge(.25)) +
    #stat_summary(color = "black", fun=mean, geom="path", size=.2) +
    #geom_flat_violin(aes(fill=StimulusType, group=StimulusType), position= position_nudge(0)) +
    geom_rangeframe(color="black", data=data.frame(epochs = c(1,2), MeanAmplitude = c(-2.5,2.5), StimulusType = c("A", "B"), Electrode = c("Fronto-Central", "Mastoids"))) +
    batheme  +
    xlab("") +
    ylab("µV") +
    scale_y_continuous(limits= c(-10,10),breaks=c(-2.5, 2.5)) +
    stat_pvalue_manual(posthoc_tests, label = "{bf_full}\n{p_full}", label.size = 2, tip.length = 0.01, linetype = "blank") +
    scale_x_discrete(expand = c(.2, .2)) +
    theme(legend.position = "none") +
    #scale_fill_brewer(palette="Dark2") + 
    scale_fill_manual(values = c("#7570b3", "#d95f02" )) +
    theme(legend.position="bottom") +
    guides(fill=guide_legend(
                 keywidth=0.2,
                 keyheight=0.2,
                 default.unit="inch")
      )

# plot_posthoc
ggsave("/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/figures/fig_posthoc.pdf", plot_posthoc, width = plot_with, height = 4, units = "in")
ggsave("/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/figures/fig_posthoc.png", plot_posthoc, width = plot_with, height = 4, units = "in",  type="cairo")

embed_fonts("/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/figures/fig_posthoc.pdf")


# Write Vars
yaml::write_yaml(variables, "/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/vars.yaml")



#### Reliability Analysis #####

df <- read.csv("out.csv") 

sb = function(n, rel, o_n) { 
  rel = (rel) / (rel * (-o_n) + rel + o_n)
  return((n * rel) / (1 + (n - 1) * rel))
  }

# split-half
gdf3 <- df %>% mutate(epochs = factor(num)) %>% mutate(soa = factor(paste(soa, "ms"))) %>% 
    filter(type == "half_1" | type == "half_2") %>%
    filter(!any(is.na(amplitude_difference))) %>%
    pivot_wider(id_cols = c(id,soa,num,run,epochs), names_from = type, values_from = amplitude_difference) %>%
    group_by(epochs, run, soa) %>% 
    summarize(cor=cor(half_1, half_2)) %>%
    mutate(rel = ( ( 2 * cor ) / (1 + cor)) ) %>%
    ungroup() %>%
    group_by(epochs, soa) %>%
    summarize(sd = sd(rel), rel = mean(rel)) %>% 
    mutate(epochs = as.numeric(as.character(epochs))) %>%
    group_by(soa)# %>%
    #filter(row_number() %% 2 == 0) 
  
gdf3 = gdf3 %>% ungroup() %>%
  mutate(real = "yes") %>%
  #add_row(soa = "100 ms", epochs = seq(100,3000,100), rel = sb(seq(100,3000,100), 0.78610510, 3000), real = "no") %>%
  add_row(soa = "150 ms", epochs = seq(1500,3000,100), rel = sb(seq(1500,3000,100), 0.7862026, 1500), real = "no")
    

plot_rel = ggplot(data=gdf3, aes(x = epochs, y = rel, fill=soa)) + 
    batheme +
    annotate('segment', x=100,xend=2500,y=.2,yend=.2, size = .02, alpha = .6) +
    annotate('segment', x=100,xend=2500,y=.4,yend=.4, size = .02, alpha = .6) +
    annotate('segment', x=100,xend=3000,y=.6,yend=.6, size = .02, alpha = .6) +
    annotate('segment', x=100,xend=3000,y=.8,yend=.8, size = .02, alpha = .6) +
    #scale_fill_brewer(palette="Set1") +
    #scale_color_brewer(palette="Set1") +
    #facet_grid(rows = vars(soa)) +
    geom_line(data = filter(gdf3, real == "yes"), aes(group=soa, color=soa), size=.75) +
    geom_line(data = filter(gdf3, real == "no"), aes(group=soa, color=soa), size=1, linetype = "dotted", show.legend = FALSE) +
    #geom_errorbar(aes(color=soa, ymin=rel-sd, ymax=rel+sd)) +
    geom_point(aes(color=soa), data = filter(gdf3, real == "yes"), show.legend = FALSE) +
    ylim(-.1,1) +
    geom_rangeframe(data=data.frame(epochs = c(100,3000), soa = "150 ms", rel = c(0,1))) + 
    #ggtitle("Split-Half Reliability") + 
    ylab(expression("Mean Split-Half Reliability")) +
    xlab(expression(N[Epochs])) + 
    labs(shape = "19")  +
    scale_x_continuous(breaks=c(100, 500, 1000, 1500, 2000, 2500, 3000)) +
    scale_y_continuous(breaks=c(0, .2, .4, .6, .8, 1)) +
    theme(legend.position = c(.875, 0.325)) + 
    scale_colour_grey(start = .5, end = .2)

ggsave("/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/figures/fig_subsample_rel.pdf", plot_rel, width = plot_with, height = 1.8, units = "in",  device=cairo_pdf)
ggsave("/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/figures/fig_subsample_rel.png", plot_rel, width = plot_with, height = 1.8, units = "in")



