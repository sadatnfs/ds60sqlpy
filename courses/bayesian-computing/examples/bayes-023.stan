transformed data {
  int N = 12;
  vector[N] y = [0.1, 0.3, 0.2, 0.5, 0.4, 0.2, -0.1, -0.2, 0, 0.2, 0.1, 0.05]';
}
parameters {
  real mu;
  real<lower=-1, upper=1> phi;
  real<lower=0> sigma;
}
model {
  mu ~ normal(0, 1);
  phi ~ normal(0, 0.5);
  sigma ~ normal(0, 0.5);
  y[1] ~ normal(mu, sigma / sqrt(1 - square(phi)));
  for (n in 2 : N)
    y[n] ~ normal(mu + phi * (y[n - 1] - mu), sigma);
}
generated quantities {
  real next_mean = mu + phi * (y[N] - mu);
  real next_outcome = normal_rng(next_mean, sigma);
  real horizon_three_mean = mu + pow(phi, 3) * (y[N] - mu);
  real horizon_three_variance = square(sigma) * (1 + square(phi) + pow(phi, 4));
  real horizon_three_outcome = normal_rng(horizon_three_mean, sqrt(horizon_three_variance));
}
