library("tidyverse")
library("cowplot")
library("gridExtra")

#setwd("./analysis")

df <- read.csv("out.csv") 

# somewhat hackish solution to:
# https://twitter.com/EamonCaddigan/status/646759751242620928
# based mostly on copy/pasting from ggplot2 geom_violin source:
# https://github.com/hadley/ggplot2/blob/master/R/geom-violin.r


"%||%" <- function(a, b) {
  if (!is.null(a)) a else b
}

geom_flat_violin <- function(mapping = NULL, data = NULL, stat = "ydensity",
                        position = "dodge", trim = TRUE, scale = "area",
                        show.legend = NA, inherit.aes = TRUE, ...) {
  layer(
    data = data,
    mapping = mapping,
    stat = stat,
    geom = GeomFlatViolin,
    position = position,
    show.legend = show.legend,
    inherit.aes = inherit.aes,
    params = list(
      trim = trim,
      scale = scale,
      ...
    )
  )
}

#' @rdname ggplot2-ggproto
#' @format NULL
#' @usage NULL
#' @export
GeomFlatViolin <-
  ggproto("GeomFlatViolin", Geom,
          setup_data = function(data, params) {
            data$width <- data$width %||%
              params$width %||% (resolution(data$x, FALSE) * 0.9)
            
            # ymin, ymax, xmin, and xmax define the bounding rectangle for each group
            data %>%
              group_by(group) %>%
              mutate(ymin = min(y),
                     ymax = max(y),
                     xmin = x,
                     xmax = x + width / 2)
            
          },
          
          draw_group = function(data, panel_scales, coord) {
            # Find the points for the line to go all the way around
            data <- transform(data, xminv = x,
                              xmaxv = x + violinwidth * (xmax - x))
            
            # Make sure it's sorted properly to draw the outline
            newdata <- rbind(plyr::arrange(transform(data, x = xminv), y),
                             plyr::arrange(transform(data, x = xmaxv), -y))
            
            # Close the polygon: set first and last point the same
            # Needed for coord_polar and such
            newdata <- rbind(newdata, newdata[1,])
            
            ggplot2:::ggname("geom_flat_violin", GeomPolygon$draw_panel(newdata, panel_scales, coord))
          },
          
          draw_key = draw_key_polygon,
          
          default_aes = aes(weight = 1, colour = "grey20", fill = "white", size = 0.5,
                            alpha = NA, linetype = "solid"),
          
          required_aes = c("x", "y")
)

raincloud_theme = theme(
text = element_text(size = 10),
axis.title.x = element_text(size = 16),
axis.title.y = element_text(size = 16),
axis.text = element_text(size = 14),
axis.text.x = element_text(angle = 45, vjust = 0.5),
legend.title=element_text(size=16),
legend.text=element_text(size=16),
legend.position = "right",
plot.title = element_text(lineheight=.8, face="bold", size = 16),
panel.border = element_blank(),
panel.grid.minor = element_blank(),
panel.grid.major = element_blank(),
axis.line.x = element_line(colour = 'black', size=0.5, linetype='solid'),
axis.line.y = element_line(colour = 'black', size=0.5, linetype='solid'))

theme_min <- function(base_size = 11, base_family = "") {

  theme_light(base_size = 11, base_family = "") +
    theme(
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.background = element_blank(),
      panel.border = element_rect(fill = NA, colour = "black", size = 1),
      strip.background = element_rect(fill = NA, colour = NA),
      strip.text.x = element_text(colour = "black", size = rel(1.2)),
      strip.text.y = element_text(colour = "black", size = rel(1.2)),
      title = element_text(size = rel(0.9)),
      axis.text = element_text(colour = "black", size = rel(0.8)),
      axis.title = element_text(colour = "black", size = rel(0.9)),
      legend.title = element_text(colour = "black", size = rel(0.9)),
      legend.key.size = unit(0.9, "lines"),
      legend.text = element_text(size = rel(0.7), colour = "black"),
      legend.key = element_rect(colour = NA, fill = NA),
      legend.background = element_rect(colour = NA, fill = NA)
    )
}

# Effects
gdf1 <- df %>% mutate(epochs = factor(num)) %>% mutate(SOA = factor(soa)) %>% 
    group_by(epochs, run, SOA) %>% 
    filter(!any(is.na(amplitude_difference))) %>%
    ungroup() %>% group_by(epochs, run, SOA) %>% 
    summarize(mean_amplitude_difference=mean(amplitude_difference)) %>% 
    mutate(mean_amplitude_difference = mean_amplitude_difference * 10e5) 

plot_e = ggplot(data=gdf1, aes(x = epochs, y = mean_amplitude_difference, fill=SOA)) + 
    scale_fill_brewer(palette="Set1") +
    scale_color_brewer(palette="Set1") +
    geom_point(aes(color=SOA), position = position_jitterdodge(dodge.width = .25, jitter.width = .25), size = .25, alpha = 1) +
    #geom_line(aes(group=interaction(run,SOA)), alpha=.2) +
    geom_boxplot(width = .6, outlier.shape = NA, alpha = 0.5) +
    #geom_flat_violin(position = position_nudge(x = .2, y = 0), alpha = .8)  + 
    theme_min() +
    ggtitle("Mean Amplitude Difference") + 
    ylab("µV") +
    xlab(expression(N[Epochs]))

# t-Values
gdf2 <- df %>% mutate(epochs = factor(num)) %>% mutate(SOA = factor(paste(soa, "ms"))) %>% 
    group_by(epochs, run, SOA) %>% 
    filter(!any(is.na(amplitude_difference))) %>%
    summarize(t_val=t.test(amplitude_difference)[["statistic"]], t_crit=qt(p = 0.95, df = t.test(amplitude_difference)[["parameter"]]))

plot_t = ggplot(data=gdf2, aes(x = epochs, y = t_val, fill=SOA)) + 
    scale_fill_brewer(palette="Set1") +
    scale_color_brewer(palette="Set1") +
    geom_point(aes(color=SOA), position = position_jitterdodge(dodge.width = .25, jitter.width = .25), size = .25, alpha = 1) +
    #geom_line(aes(group=interaction(run,soa)), alpha=.2) +
    geom_boxplot(width = .6, outlier.shape = NA, alpha = 0.5) +
    #geom_flat_violin(position = position_nudge(x = .2, y = 0), alpha = .8)  + 
    theme_min() +
    ggtitle("t-Values") + 
    ylab(expression(italic(t))) +
    xlab(expression(N[Epochs])) + 
    geom_hline(yintercept=1.72, linetype="dashed", alpha=1, size=.75) +
    annotate("text", x = 12.2, y = 1.72, vjust=1.6, size=4, label = expression(bolditalic(t[crit]))) +
    labs(shape = "19") 


# extract a legend that is laid out horizontally
legend <- get_legend(
  plot_t + theme(legend.position="bottom")
)


plot_final = plot_grid(
  plot_e + theme(legend.position="none", text = element_text(size=8)),
  plot_t + theme(legend.position="none"),
  legend = legend,
  align = 'vh',
  #labels = c("A", "B"),
  hjust = -1,
  nrow = 3,
  ncol=1,
  rel_heights = c(1,1, .2)
)

plot_final

gdf <- df %>% mutate(epochs = factor(num)) %>% mutate(SOA = factor(soa)) %>% 
    group_by(epochs, run, SOA) %>% 
    summarize(mean_amplitude_difference=mean(amplitude_difference)) %>% 
    group_by(epochs, SOA) %>% 
    summarize(mean_amplitude_difference=sd(mean_amplitude_difference)) %>% 
    mutate(mean_amplitude_difference = mean_amplitude_difference * 10e5) 

ggplot(data=gdf, aes(x = epochs, y = mean_amplitude_difference, group=soa, color=soa)) + 
    geom_line()


ggsave("/home/marc/ba-thesis/input/figures/fig3.png", plot_final, width = 6.25, height = 4.5, units = "in")
