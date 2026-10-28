transformed data {
  int N = 8;
  vector[N] x = [-2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2]';
  array[N] int y = {0, 0, 1, 0, 1, 0, 1, 1};
}
parameters {
  real alpha;
  real beta;
}
model {
  alpha ~ normal(0, 1.5);
  beta ~ normal(0, 2.5);
  y ~ bernoulli_logit(alpha + beta * x);
}
generated quantities {
  vector[N] probability = inv_logit(alpha + beta * x);
  vector[N] log_lik;
  array[N] int y_rep;
  for (n in 1 : N) {
    log_lik[n] = bernoulli_logit_lpmf(y[n] | alpha + beta * x[n]);
    y_rep[n] = bernoulli_rng(probability[n]);
  }
  real probability_at_zero = inv_logit(alpha);
}
