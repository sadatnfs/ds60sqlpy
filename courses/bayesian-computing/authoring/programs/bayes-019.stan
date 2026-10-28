// Two independent copies of one posterior compare parameterizations.
transformed data {
  int N = 5;
  array[N] int y = {0, 1, 2, 0, 3};
  real prior_shape = 2;
  real prior_rate = 1;
}
parameters {
  real<lower=0> lambda;
  real z;
}
model {
  // Declared constraints have their internal Jacobian handled by Stan.
  lambda ~ gamma(prior_shape, prior_rate);
  y ~ poisson(lambda);
  // The manually introduced log-rate transform needs its own Jacobian.
  target += gamma_lpdf(exp(z) | prior_shape, prior_rate) + z;
  target += poisson_lpmf(y | exp(z));
}
generated quantities {
  real lambda_from_z = exp(z);
  real exact_posterior_mean = (prior_shape + sum(y)) / (prior_rate + N);
  real exact_posterior_variance = (prior_shape + sum(y)) / square(prior_rate + N);
}
