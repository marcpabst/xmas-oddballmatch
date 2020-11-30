library(tidyverse)

data = readr::read_csv("../data/sequences.csv") %>% 
    mutate(Condition = factor(Condition)) %>%
    mutate(Time = as.numeric(Time)) %>%
    mutate(Voltage = as.numeric(Voltage))

ggplot(data=filter(data, Electrode == "FZ"), aes(x=Time, y=Voltage, color=Condition)) +
    facet_grid(rows=vars(SOA)) +
    geom_line()
