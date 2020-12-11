#* Load requeired packages
library(tidyverse) # data mangling
library(lme4) # mixed models
library(lmerTest) # implements tests for lme4
library(ggpubr) # extenden plotting for ggplot
library(rstatix) # pip-firnedly statistical tests
library(xtable) # create tables
library(huxtable) # create more aewsome tables
library(stringr) # 
library(lemon) # provides repeadted axis for facet_grid()
library(ggthemes) # for tufte theme
library(Cairo) # better hadnling of PDFs
library(extrafont) # handling fonts for PDFs

source("plot_functions.R") # custom functions for plotting
source("res/themes.R") # custom themes
source("res/report.R") # custom reporting functions
source("res/best.R") # custom reporting functions

#### ----------------- LOAD DATA ----------------------------------------------------------
tables_path <- "/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/tables"

mean_amplitudes_df <- readr::read_csv("../data/mean_amplitudes.csv")
mean_amplitudes_df <- mean_amplitudes_df %>%
  mutate(Participant = factor(Participant), SOA = factor(SOA), Electrode = factor(Electrode), Condition = factor(Condition), StimulusType = factor(StimulusType))

mean_amplitudes_df2 <- readr::read_csv("../data/mean_amplitudes2.csv")
mean_amplitudes_df2 <- mean_amplitudes_df2 %>%
  mutate(Participant = factor(Participant), SOA = factor(SOA), Electrode = factor(Electrode), Condition = factor(Condition), StimulusType = factor(StimulusType))

mean_amplitudes_df_random_alt <- readr::read_csv("../data/mean_amplitudes_random_alt.csv")
mean_amplitudes_df_random_alt <- mean_amplitudes_df_random_alt %>%
  mutate(Participant = factor(Participant), SOA = factor(SOA), Electrode = factor(Electrode), Condition = factor(Condition), StimulusType = factor(StimulusType))


n1_mean_amplitudes_df <- readr::read_csv("../data/n1_mean_amplitudes.csv")
n1_mean_amplitudes_df <- n1_mean_amplitudes_df %>% mutate(Participant = factor(Participant), SOA = factor(SOA), Electrode = factor(Electrode), Condition = factor(Condition), StimulusType = factor(StimulusType))
n1_mean_amplitudes_df

#* this variable will hold results that will be exported later
variables = list()


#### FORMATTING ###

plot_with = 6.25


#### ------------------ DESCRIBE DATA ----------------------------------------------------------

# Description Table for Frontocentral Electrodes
desc_table_frontocentral = mean_amplitudes_df %>% filter(Electrode == "fronto_pooled") %>% droplevels() %>%
    group_by(SOA, Condition, StimulusType) %>%
    summarise(Mean = mean(MeanAmplitude)*10e5, SD = sd(MeanAmplitude)*10e5) %>%
    hux() %>%
    merge_repeated_rows(col=c(1,2)) %>%
    theme_article()

#* Description Table for Mastoid Electrodes
desc_table_mastoids = mean_amplitudes_df %>% filter(Electrode == "mastoids_pooled") %>% droplevels() %>%
    group_by(SOA, Condition, StimulusType) %>%
    summarise(Mean = mean(MeanAmplitude)*10e5, SD = sd(MeanAmplitude)*10e5) %>% ungroup() %>%
    select(Mean, SD) %>%
    hux() %>%
    merge_repeated_rows(col=c(1,2)) %>%
    theme_article()

#* Combine Tables and Export to LaTex
desc_table_final = cbind(desc_table_frontocentral,desc_table_mastoids) %>%
    set_caption("Means and standard deviations for condition, stimulus type and electrodes.")

write(to_latex(desc_table_final), paste(tables_path, "desc_table.tex", sep="/"))

#* Description Deltas
desc_table_intern1 = mean_amplitudes_df %>% filter(Electrode == "fronto_pooled") %>% droplevels() %>%
    group_by(SOA, Condition, StimulusType) %>%
    summarise(Mean = mean(MeanAmplitude)*10e5, SD = sd(MeanAmplitude)*10e5)  %>% ungroup() %>%
    group_by(SOA, Condition) %>%
    summarise(delta_mean = Mean[[2]] - Mean[[1]])  %>% ungroup()

# TODO: Re-do to use reporting function
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


#### ------------------------------------- ANOVAS ------------------------------------------------ ####
##### ANOVAS for A-A-A-A-|B| vs A-A-A-|A|-A
# The follwing ANOVAS will be computed:
# 1. 100 ms, Condition x Electrode x StimulusType
# 2. 100 ms + frontal electrodes, Condition x StimulusType
# 3. 100 ms + mastoid electrodes, Condition x StimulusType
# 4. 150 ms, Condition x Electrode x StimulusType
# 5. 150 ms + frontal electrodes, Condition x StimulusType
# 6. 150 ms + mastoid electrodes, Condition x StimulusType

#* ANOVA for 100 ms, Condition x Electrode x StimulusType
anova_02_100_data = mean_amplitudes_df %>% 
                    filter(SOA == "100") %>% filter(Electrode == "fronto_pooled" | Electrode == "mastoids_pooled") %>% 
                    droplevels() %>% mutate(MeanAmplitude = MeanAmplitude*10e5)

anova_02_100_table = anova_02_100_data %>% 
                      anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType, Electrode)) %>%
                      get_anova_table(correction = "auto")

anova_02_100_table$Effect = str_replace_all(anova_02_100_table$Effect, ":", " x ") # fix effect collumns
class(anova_02_100_table) = "data.frame" # fix tidýverse problem

#* Reporting
variables$anova_02_100_condition = anova_02_100_table %>% 
                                   filter(Effect == "Condition") %>% report_anova()
variables$anova_02_100_stimulustype = anova_02_100_table %>% 
                                   filter(Effect == "StimulusType") %>% report_anova()
variables$anova_02_100_electrode = anova_02_100_table %>% 
                                   filter(Effect == "Electrode") %>% report_anova()
variables$anova_02_100_condition_stimulustype = anova_02_100_table %>% 
                                   filter(Effect == "Condition x StimulusType") %>% report_anova()
variables$anova_02_100_condition_electrode = anova_02_100_table %>% 
                                   filter(Effect == "Condition x Electrode") %>% report_anova()
variables$anova_02_100_stimulustype_electrode = anova_02_100_table %>%
                                   filter(Effect == "StimulusType x Electrode") %>% report_anova()
variables$anova_02_100_condition_stimulustype_electrode = anova_02_100_table %>% 
                                   filter(Effect == "Condition x StimulusType x Electrode") %>% report_anova()

print(xtable(anova_02_100_table), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", 
      file = paste(tables_path, "anova_01_100.tex", sep="/"))

#* ANOVA for 100 ms + frontal electrodes, Condition x StimulusType
anova_01_100_data = mean_amplitudes_df %>% filter(SOA == "100" & Electrode == "fronto_pooled") %>% droplevels() 
anova_01_100_table =    anova_01_100_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                        get_anova_table()
anova_01_100_table$Effect = str_replace_all(anova_01_100_table$Effect, ":", " x ")
class(anova_01_100_table) = "data.frame" # fix tidýverse problem


variables$anova_01_100_condition = anova_01_100_table %>% 
                                   filter(Effect == "Condition") %>% report_anova()
variables$anova_01_100_stimulustype = anova_01_100_table %>% 
                                   filter(Effect == "StimulusType") %>% report_anova()
variables$anova_01_100_condition_stimulustype = anova_01_100_table %>% 
                                   filter(Effect == "Condition x StimulusType") %>% report_anova()
caption  = "Results of the 3-way ANOVA (condition x stimulus x electrode) for repeated measures conducted on the mean ERP-amplitudes (time window 111 - 161 ms) at electrode Fz (upper section). The significant interaction between the three factors included was further analyzed by 2-way ANOVAS (stimulus x electrode) conducted separately for the random condition (middle section) and the predictable condition (lower section)."
print(xtable(anova_01_100_table, correction = "auto", caption = caption), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova_02_100.tex", sep="/"))

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

#* ANOVA for 100 ms + mastoid electrodes, Condition x StimulusType
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

#* ANOVA for 150 ms + frontal electrodes, Condition x StimulusType
anova_01_150_data = mean_amplitudes_df %>% filter(SOA == "150" & Electrode == "fronto_pooled") %>% droplevels() 
anova_01_150_table =    anova_01_150_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                        get_anova_table()
anova_01_150_table$Effect = str_replace_all(anova_01_150_table$Effect, ":", " x ")
variables$anova_01_150_condition = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_150_table$DFn[[1]], anova_01_150_table$DFd[[1]], anova_01_150_table$F[[1]], anova_01_150_table$p[[1]])
variables$anova_01_150_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_150_table$DFn[[2]], anova_01_150_table$DFd[[2]], anova_01_150_table$F[[2]], anova_01_150_table$p[[2]])
variables$anova_01_150_condition_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova_01_150_table$DFn[[3]], anova_01_150_table$DFd[[3]], anova_01_150_table$F[[3]], anova_01_150_table$p[[3]])
print(xtable(anova_01_150_table, correction = "auto"), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova_01_150.tex", sep="/"))



anova_03_150_data = mean_amplitudes_df %>% filter(SOA == "150" & Electrode == "fronto_pooled") %>% droplevels() 
anova_03_150_table = anova_03_150_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova_03_150_table$Effect = str_replace_all(anova_03_150_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 150 ms (only fronto)."
print(xtable(anova_03_150_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova_03_150.tex", sep="/"))

class(anova_03_150_table) = "data.frame" # fix tidýverse problem


variables$anova_03_150_fronto_condition = anova_03_150_table %>% 
                                   filter(Effect == "Condition") %>% report_anova()
variables$anova_03_150_fronto_stimulustype = anova_03_150_table %>% 
                                   filter(Effect == "StimulusType") %>% report_anova()
variables$anova_03_150_fronto_condition_stimulustype = anova_03_150_table %>% 
                                   filter(Effect == "Condition x StimulusType") %>% report_anova()

#* ANOVA for 150 ms + mastoid electrodes, Condition x StimulusType
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

#* Create More Complex Tables

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

                        set_caption(anova_03_full_caption) %>%

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


##### ANOVAS for A-A-A-A-|A| vs A-A-A-|A|-A

#* ANOVA for 100 ms + frontal electrodes, Condition x StimulusType
anova2_01_100_data = mean_amplitudes_df2 %>% filter(SOA == "100" & Electrode == "fronto_pooled") %>% droplevels() 
anova2_01_100_table =    anova2_01_100_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                        get_anova_table()
anova2_01_100_table$Effect = str_replace_all(anova2_01_100_table$Effect, ":", " x ")

variables$anova2_01_100_condition = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova2_01_100_table$DFn[[1]], anova2_01_100_table$DFd[[1]], anova2_01_100_table$F[[1]], anova2_01_100_table$p[[1]])
variables$anova2_01_100_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova2_01_100_table$DFn[[2]], anova2_01_100_table$DFd[[2]], anova2_01_100_table$F[[2]], anova2_01_100_table$p[[2]])
variables$anova2_01_100_condition_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova2_01_100_table$DFn[[3]], anova2_01_100_table$DFd[[3]], anova2_01_100_table$F[[3]], anova2_01_100_table$p[[3]])
caption  = "Results of the 3-way ANOVA (condition x stimulus x electrode) for repeated measures conducted on the mean ERP-amplitudes (time window 111 - 161 ms) at electrode Fz (upper section). The significant interaction between the three factors included was further analyzed by 2-way ANOVAS (stimulus x electrode) conducted separately for the random condition (middle section) and the predictable condition (lower section)."
print(xtable(anova2_01_100_table, correction = "auto", caption = caption), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova2_02_100.tex", sep="/"))

anova2_03_100_data = mean_amplitudes_df2 %>% filter(SOA == "100" & Electrode == "fronto_pooled") %>% droplevels() 
anova2_03_100_table = anova2_03_100_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova2_03_100_table$Effect = str_replace_all(anova2_03_100_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 100 ms (only fronto)"
print(xtable(anova2_03_100_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova2_03_100.tex", sep="/"))

variables$anova2_03_100_fronto_condition = sprintf(anova_template, anova2_03_100_table$DFn[[1]], anova2_03_100_table$DFd[[1]], anova2_03_100_table$F[[1]], anova2_03_100_table$p[[1]])
variables$anova2_03_100_fronto_stimulustype = sprintf(anova_template, anova2_03_100_table$DFn[[2]], anova2_03_100_table$DFd[[2]], anova2_03_100_table$F[[2]], anova2_03_100_table$p[[2]])
variables$anova2_03_100_fronto_condition_stimulustype = sprintf(anova_template, anova2_03_100_table$DFn[[3]], anova2_03_100_table$DFd[[3]], anova2_03_100_table$F[[3]], anova2_03_100_table$p[[3]])

#* ANOVA for 100 ms + mastoid electrodes, Condition x StimulusType
anova2_04_100_data =  mean_amplitudes_df2 %>% filter(SOA == "100" & Electrode == "mastoids_pooled") %>% droplevels() 
anova2_04_100_table = anova2_04_100_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova2_04_100_table$Effect = str_replace_all(anova2_04_100_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 100 ms with non-pooled electrodes"
print(xtable(anova2_04_100_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova2_04_100.tex", sep="/"))

variables$anova2_03_100_mastoids_condition = sprintf(anova_template, anova2_04_100_table$DFn[[1]], anova2_04_100_table$DFd[[1]], anova2_04_100_table$F[[1]], anova2_04_100_table$p[[1]])
variables$anova2_03_100_mastoids_stimulustype = sprintf(anova_template, anova2_04_100_table$DFn[[2]], anova2_04_100_table$DFd[[2]], anova2_04_100_table$F[[2]], anova2_04_100_table$p[[2]])
variables$anova2_03_100_mastoids_condition_stimulustype = sprintf(anova_template, anova2_04_100_table$DFn[[3]], anova2_04_100_table$DFd[[3]], anova2_04_100_table$F[[3]], anova2_04_100_table$p[[3]])

#* ANOVA for 150 ms + frontal electrodes, Condition x StimulusType
anova2_01_150_data = mean_amplitudes_df2 %>% filter(SOA == "150" & Electrode == "fronto_pooled") %>% droplevels() 
anova2_01_150_table =    anova2_01_150_data %>% 
                        anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                        get_anova_table()
anova2_01_150_table$Effect = str_replace_all(anova2_01_150_table$Effect, ":", " x ")
variables$anova2_01_150_condition = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova2_01_150_table$DFn[[1]], anova2_01_150_table$DFd[[1]], anova2_01_150_table$F[[1]], anova2_01_150_table$p[[1]])
variables$anova2_01_150_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova2_01_150_table$DFn[[2]], anova2_01_150_table$DFd[[2]], anova2_01_150_table$F[[2]], anova2_01_150_table$p[[2]])
variables$anova2_01_150_condition_stimulustype = sprintf("$F(%.0f,%.0f) = %.2f$, $p = %.4f$", anova2_01_150_table$DFn[[3]], anova2_01_150_table$DFd[[3]], anova2_01_150_table$F[[3]], anova2_01_150_table$p[[3]])
print(xtable(anova2_01_150_table, correction = "auto"), include.rownames = F, tabular.environment = "tabulary", width = "\\textwidth", file = paste(tables_path, "anova2_01_150.tex", sep="/"))



anova2_03_150_data = mean_amplitudes_df2 %>% filter(SOA == "150" & Electrode == "fronto_pooled") %>% droplevels() 
anova2_03_150_table = anova2_03_150_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova2_03_150_table$Effect = str_replace_all(anova2_03_150_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 150 ms (only fronto)."
print(xtable(anova2_03_150_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova2_03_150.tex", sep="/"))

variables$anova2_03_150_fronto_condition = sprintf(anova_template, anova2_03_150_table$DFn[[1]], anova2_03_150_table$DFd[[1]], anova2_03_150_table$F[[1]], anova2_03_150_table$p[[1]])
variables$anova2_03_150_fronto_stimulustype = sprintf(anova_template, anova2_03_150_table$DFn[[2]], anova2_03_150_table$DFd[[2]], anova2_03_150_table$F[[2]], anova2_03_150_table$p[[2]])
variables$anova2_03_150_fronto_condition_stimulustype = sprintf(anova_template, anova2_03_150_table$DFn[[3]], anova2_03_150_table$DFd[[3]], anova2_03_150_table$F[[3]], anova2_03_150_table$p[[3]])

#* ANOVA for 150 ms + mastoid electrodes, Condition x StimulusType
anova2_04_150_data =  mean_amplitudes_df2 %>% filter(SOA == "150" & Electrode == "mastoids_pooled") %>% droplevels() 
anova2_04_150_table = anova2_04_150_data %>% 
                     anova_test(dv = MeanAmplitude,  wid = Participant, within = c(Condition, StimulusType)) %>%
                     get_anova_table(correction = "auto")
anova2_04_150_table$Effect = str_replace_all(anova2_04_150_table$Effect, ":", " x ")
caption  = "Results from two-way ANOVA for 150 ms (only mastioids)."
print(xtable(anova2_04_150_table, caption=caption), include.rownames = F, tabular.environment = "tabulary", booktabs = TRUE, width = "\\textwidth", file = paste(tables_path, "anova2_04_150.tex", sep="/"))

variables$anova2_03_150_mastoids_condition = sprintf(anova_template, anova2_04_150_table$DFn[[1]], anova2_04_150_table$DFd[[1]], anova2_04_150_table$F[[1]], anova2_04_150_table$p[[1]])
variables$anova2_03_150_mastoids_stimulustype = sprintf(anova_template, anova2_04_150_table$DFn[[2]], anova2_04_150_table$DFd[[2]], anova2_04_150_table$F[[2]], anova2_04_150_table$p[[2]])
variables$anova2_03_150_mastoids_condition_stimulustype = sprintf(anova_template, anova2_04_150_table$DFn[[3]], anova2_04_150_table$DFd[[3]], anova2_04_150_table$F[[3]], anova2_04_150_table$p[[3]])

#* Create More Complex Tables

anova2_03_full_caption  = "Results of the 2-way ANOVA (condition x stimulus type) for repeated measures. Only fronto included."

anova2_03_full_table_1 = rbind(anova2_03_100_table %>% add_column(Electrodes = "Frontal", .before = 1), anova2_04_100_table %>% add_column(Electrodes = "Mastoids", .before =1)) 
anova2_03_full_table_2 = rbind(anova2_03_150_table %>% add_column(Electrodes = "Frontal", .before = 1), anova2_04_150_table %>% add_column(Electrodes = "Mastoids", .before =1)) 

anova2_03_full_table = rbind(anova2_03_full_table_1 %>% add_column(SOA = "100 ms", .before = 1), anova2_03_full_table_2 %>% add_column(SOA = "150 ms", .before =1)) %>%  hux() %>%
                        set_number_format(col=7, value=list(fm_pvalue)) %>%
                        merge_repeated_rows(col=c(1,2)) %>%
                        set_rotation(col=c(1,2), value=90) %>%
                        set_valign(col=c(1,2), value="middle") %>%
                        set_header_rows(1, TRUE) %>%
                        set_contents(1,1, value = "") %>%
                        set_contents(1,2, value = "") %>%

                        set_caption(anova2_03_full_caption) %>%

                        set_bottom_padding(row=4, value=8) %>%

                        set_top_padding(row=5, value=8) %>%
                        set_bottom_padding(row=7, value=15) %>%

                        set_top_padding(row=8, value=15) %>%
                        set_bottom_padding(row=10, value=8) %>%

                        set_top_padding(row=11, value=8) %>%

                        #set_bottom_padding(row=8, value=15) %>%
                        #set_top_padding(row=9, value=15) %>%
                        theme_article()


write(to_latex(anova2_03_full_table), paste(tables_path, "anova2_03_full.tex", sep="/"))


#### POST-HOC TESTS ####

posthoc_data = mean_amplitudes_df %>% filter(Electrode == "fronto_pooled" | Electrode == "mastoids_pooled") %>% droplevels() %>% 
       mutate(MeanAmplitude = MeanAmplitude*10e5) %>%
       mutate(SOA = fct_relabel(SOA, ~ paste(., "ms"))) %>%
       mutate(StimulusType = fct_relabel(StimulusType, ~ paste(., "tone"))) %>% 
       mutate(Electrode = fct_recode(Electrode, "Fronto-Central" = "fronto_pooled", "Mastoids" = "mastoids_pooled" )) 

posthoc_tests = posthoc_data %>%
                filter(Electrode == "Fronto-Central" & SOA == "100 ms") %>%
                group_by(SOA, Condition, Electrode) %>%
                bayesian_t_test(data =., MeanAmplitude ~ StimulusType, paired=T, detailed=T) %>% # verry hacky !
                rename(bf = statistic)
  
  
posthoc_tests = posthoc_data %>% 
                filter(Electrode == "Fronto-Central" & SOA == "100 ms") %>%
                group_by(SOA, Condition, Electrode) %>%
                t_test(data =., MeanAmplitude ~ StimulusType, paired=T, detailed=T) %>%
                left_join(posthoc_tests, by = c("SOA", "Condition", "Electrode", "group1", "group2"))  %>%
                adjust_pvalue(method = "fdr") %>%
                add_significance("p.adj") %>%
                add_xy_position(x = "Electrode") %>%
                mutate(p_full = fm_pvalue_full(p.adj)) %>%
                mutate(bf_full = fm_bf10_full(bf)) %>%
                mutate(y.position = 7.5)

print(posthoc_tests)

variables$posthoc_pred_a_b_fronto_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "predictable" & Electrode == "Fronto-Central"))
#variables$posthoc_pred_a_b_mast_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "predictable" & Electrode == "Mastoids"))

variables$posthoc_rand_a_b_fronto_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "random" & Electrode == "Fronto-Central"))
#variables$posthoc_rand_a_b_mast_100 = report_ttest(filter(posthoc_tests, SOA == "100 ms" & Condition == "random" & Electrode == "Mastoids"))

#variables$posthoc_pred_a_b_fronto_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "predictable" & Electrode == "Fronto-Central"))
#variables$posthoc_pred_a_b_mast_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "predictable" & Electrode == "Mastoids"))

#variables$posthoc_rand_a_b_fronto_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "random" & Electrode == "Fronto-Central"))
#variables$posthoc_rand_a_b_mast_150 = report_ttest(filter(posthoc_tests, SOA == "150 ms" & Condition == "random" & Electrode == "Mastoids"))


plot_posthoc = ggplot(aes(y = MeanAmplitude, x = Electrode), data = posthoc_data) + 
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



#### COMPARE ALTERNATIVE RANDOM ####

posthoc_data = mean_amplitudes_df_random_alt %>% 
       filter(Condition == "random") %>%
       filter(Electrode == "fronto_pooled") %>% droplevels() %>% 
       mutate(MeanAmplitude = MeanAmplitude*10e5) %>%
       mutate(SOA = fct_relabel(SOA, ~ paste(., "ms"))) %>%
       mutate(StimulusType = fct_relabel(StimulusType, ~ paste(., "tone"))) %>% 
       mutate(Electrode = fct_recode(Electrode, "Fronto-Central" = "fronto_pooled")) 

posthoc_tests = posthoc_data %>%
                group_by(SOA, Condition, Electrode) %>%
                bayesian_t_test(data =., MeanAmplitude ~ StimulusType, paired=T, detailed=T) %>% # verry hacky !
                rename(bf = statistic)
  
posthoc_tests = posthoc_data %>% 
                group_by(SOA, Condition, Electrode) %>%
                t_test(data =., MeanAmplitude ~ StimulusType, paired=T, detailed=T) %>%
                left_join(posthoc_tests, by = c("SOA", "Condition", "Electrode", "group1", "group2"))  %>%
                adjust_pvalue(method = "fdr") %>%
                add_significance("p.adj") %>%
                add_xy_position(x = "Electrode") %>%
                mutate(p_full = fm_pvalue_full(p.adj)) %>%
                mutate(bf_full = fm_bf10_full(bf)) %>%
                mutate(y.position = 7.5)

variables$random_alternative_contrast_100_a_b = posthoc_tests %>% filter(SOA=="100 ms") %>% report_ttest()
print(posthoc_tests)


#### Reliability Analysis #####

df <- read.csv("out.csv") 

sb = function(n, rel, o_n) { 
  rel = (rel) / (rel * (-o_n) + rel + o_n)
  return((n * rel) / (1 + (n - 1) * rel))
  }

sb2 = function(pxx) {
    return( (2*pxx) / (1+pxx) )
}

# split-half
gdf3 <- df %>% mutate(epochs = factor(num)) %>% mutate(soa = factor(paste(soa, "ms"))) %>% 
    mutate(maxrow = ifelse(soa=="150 ms", 1250, 2500)) %>%
    mutate(minrow = ifelse(soa=="150 ms", 100, 100)) %>%
    filter(num <= maxrow & num >= minrow) %>%
    #spread(type, amplitude_difference) %>%
    pivot_wider(id_cols = c(id,soa,num,run,epochs,stimtype), names_from = type, values_from = amplitude_difference) %>%
    group_by(epochs, run, soa, stimtype) %>% 
    summarize(pxx = cor(half_1, half_2)) %>% 
    ungroup() %>%
    mutate(rel = sb2(pxx)) %>%
    group_by(epochs, soa, stimtype) %>%
    dplyr::summarize(sd = sd(rel), rel = mean(rel), pxx = mean(pxx)) %>% 
    mutate(epochs = as.numeric(as.character(epochs))) %>%
    group_by(soa, stimtype) %>%
    #filter(row_number() %% 2 == 0) %>%
    ungroup()


gdf3_extrapolate = tibble(soa = "150 ms", epochs = seq(1100,2500,100), rel = sb(seq(1100,2500,100), 0.846, 1200), cor = 0, real = "no", stimtype = "B") %>%
                  add_row(soa = "150 ms", epochs = seq(1100,2500,100), rel = sb(seq(1100,2500,100), 0.794, 1100), cor = 0, real = "no", stimtype = "A")


 
plot_rel = ggplot(data=gdf3, aes(x = epochs, y = rel, fill=soa)) + 
    batheme +
    annotate('segment', x=100,xend=2000,y=.2,yend=.2, size = .02, alpha = .6) +
    annotate('segment', x=100,xend=2000,y=.4,yend=.4, size = .02, alpha = .6) +
    annotate('segment', x=100,xend=2500,y=.6,yend=.6, size = .02, alpha = .6) +
    annotate('segment', x=100,xend=2500,y=.8,yend=.8, size = .02, alpha = .6) +
    #scale_fill_brewer(palette="Set1") +
    #scale_color_brewer(palette="Set1") +
    #facet_grid(rows = vars(soa)) +
    geom_line(data = gdf3, aes(group=interaction(soa,stimtype), color=soa, linetype=stimtype), size=.75) +
    geom_line(data = gdf3_extrapolate, aes(group=interaction(soa,stimtype), color=soa, linetype=stimtype), size=.35, show.legend = FALSE) +
    #geom_errorbar(aes(color=soa, ymin=rel-sd, ymax=rel+sd)) +
    geom_point(aes(color=soa), data = gdf3, show.legend = FALSE) +
    ylim(-.1,1) +
    geom_rangeframe(data=data.frame(epochs = c(100,2500), soa = "150 ms", pxx = c(0,1), rel = c(0,1))) + 
    #ggtitle("Split-Half Reliability") + 
    ylab(expression("Mean Split-Half Reliability")) +
    xlab(expression(N[Epochs])) + 
    labs(shape = "19")  +
    scale_x_continuous(breaks=c(100, 500, 1000, 1500, 2000, 2500)) +
    scale_y_continuous(breaks=c(0, .2, .4, .6, .8, 1)) +
    theme(legend.position = c(.850, 0.325)) + 
    scale_colour_grey(start = .5, end = .2)

ggsave("/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/figures/fig_subsample_rel.pdf", plot_rel, width = plot_with, height = 2, units = "in",  device=cairo_pdf)
ggsave("/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/figures/fig_subsample_rel.png", plot_rel, width = plot_with, height = 2, units = "in")




# Write Vars
yaml::write_yaml(variables, "/media/marc/Medien/xmas-oddballmatch/ba-thesis/input/vars.yaml")
