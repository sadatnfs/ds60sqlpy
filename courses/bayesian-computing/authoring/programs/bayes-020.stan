transformed data {
  int J = 3;
  int N = 10;
  array[N] int group = {1, 1, 2, 2, 2, 3, 3, 3, 3, 3};
  vector[N] y = [-2, -1.5, -0.4, 0, 0.3, 0.8, 1.2, 1.1, 0.9, 1]';
  real observation_sd = 0.5;
}
parameters {
  real mu;
  real<lower=0> tau;
  vector[J] z;
}
transformed parameters {
  vector[J] theta = mu + tau * z;
}
model {
  mu ~ normal(0, 2);
  tau ~ normal(0, 1);
  z ~ std_normal();
  for (n in 1 : N)
    y[n] ~ normal(theta[group[n]], observation_sd);
}
generated quantities {
  real new_group_mean = normal_rng(mu, tau);
  real known_group_outcome = normal_rng(theta[1], observation_sd);
  vector[N] log_lik;
  for (n in 1 : N)
    log_lik[n] = normal_lpdf(y[n] | theta[group[n]], observation_sd);
}
