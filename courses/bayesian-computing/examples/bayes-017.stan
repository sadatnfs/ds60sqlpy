// A self-contained classroom model. External project uses a separate data block.
transformed data {
  int N = 5;
  vector[N] y = [1.0, 1.5, 2.0, 2.5, 3.0]';
  real prior_mean = 0;
  real prior_sd = 2;
  real observation_sd = 1;
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
  real posterior_variance = inv(inv_square(prior_sd) + N / square(observation_sd));
  real posterior_mean = posterior_variance
                        * (prior_mean / square(prior_sd) + sum(y) / square(observation_sd));
  vector[N] log_lik;
  for (n in 1 : N)
    log_lik[n] = normal_lpdf(y[n] | mu, observation_sd);
}
