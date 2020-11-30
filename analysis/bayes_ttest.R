library(rstan)
library(bridgesampling)

rstan_options("auto_write" = TRUE)

  # models
  H0spec = '
    data {
      int n;
      vector[n] y;
    }
    parameters {
      real<lower=0> sigma_squared; // variance
    }
    model {
      target += log(1/sigma_squared); // Jeffreys prior on sigma2
      target += normal_lpdf(y | 0, sqrt(sigma_squared)); // likelihood
    }
    '
    H1spec = '
    data {
      int n; 
      vector[n] y;
      real r;
    }

    parameters {
      real delta; // the difference
      real<lower=0> sigma_squared; // variance
    }
    model {
      target += cauchy_lpdf(delta | 0, r); // Cauchy prior on 
      target += log(1/sigma_squared); // Jeffreys prior on sigma_squared
      target += normal_lpdf(y | delta*sqrt(sigma_squared), sqrt(sigma_squared));  // likelihood
    }
    '
    # compile models
    H0model <- stan_model(model_code = H0spec, model_name="stanmodel1")
    H1model <- stan_model(model_code = H1spec, model_name="stanmodel2")


one_sample_test_bayes = function(y) {


    n = length(y)

    H0fit <- sampling(H0model, data = list(y = y, n = n),
                          iter = 20000, warmup = 1000, chains = 4, cores = 1,
                          control = list(adapt_delta = .99))
                          
    H1fit <- sampling(H1model, data = list(y = y, n = n, r = 1/sqrt(2)),
                          iter = 20000, warmup = 1000, chains = 4, cores = 1,
                          control = list(adapt_delta = .99))
    print(H1fit)

    H0 <- bridge_sampler(H0fit, silent = TRUE)
    H1 <- bridge_sampler(H1fit, silent = TRUE)

    

    BF10 <- bf(H1, H0)
    #return(BF10)

    x = list(as.numeric(BF10$bf)[1])
    attr(x, "names") = "statistic"
    attr(x, "class") = "htest"
    return(x)

}


y = c(3,4,3,6,7,5,3,2,4,3,3)
   

res1 = one_sample_test_bayes(y)
res2 = ttestBF(y)
