
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
    ttest_template = "$t(%i) = %.2f$, $%s$, $CI_{.95} = [%.2f,%.2f], BF_{10} = %.2f$"
    return( sprintf(ttest_template, 
                test_row %>% pull(df),
                test_row %>% pull(statistic),
                test_row %>% pull(p.adj) %>% fm_pvalue_full(), # already formatted
                test_row %>% pull(conf.low),
                test_row %>% pull(conf.high),
                test_row %>% pull(bf)
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
