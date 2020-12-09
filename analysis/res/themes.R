
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

