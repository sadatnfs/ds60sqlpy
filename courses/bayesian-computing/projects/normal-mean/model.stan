data {
  int<lower=1> N;
  vector[N] y;
  real prior_mean;
  real<lower=0> prior_sd;
  real<lower=0> observation_sd;
}
parameters {
  real mu;
}
model {
  mu ~ normal(prior_mean, prior_sd);
  y ~ normal(mu, observation_sd);
}
generated quantities {
  real y_rep = normal_rng(mu, observation_sd);
  vector[N] log_lik;
  for (n in 1 : N)
    log_lik[n] = normal_lpdf(y[n] | mu, observation_sd);
}
