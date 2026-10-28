transformed data {
  int N = 5;
  matrix[N, 2] X;
  vector[N] y = [-1.8, -0.7, 0.4, 1.8, 2.9]';
  for (n in 1 : N) {
    X[n, 1] = 1;
    X[n, 2] = n - 3;
  }
}
parameters {
  vector[2] beta;
  real<lower=0> sigma;
}
transformed parameters {
  vector[N] mu = X * beta;
}
model {
  beta ~ normal(0, 2);
  sigma ~ normal(0, 0.5);
  y ~ normal(mu, sigma);
}
generated quantities {
  real new_mean = beta[1] + 0.5 * beta[2];
  real new_outcome = normal_rng(new_mean, sigma);
  vector[N] log_lik;
  for (n in 1 : N)
    log_lik[n] = normal_lpdf(y[n] | mu[n], sigma);
}
