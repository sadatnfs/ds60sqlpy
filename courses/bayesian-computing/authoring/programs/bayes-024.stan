transformed data {
  int N = 8;
  vector[N] time = [1.1, 2.3, 3, 4, 5.2, 6, 8, 9]';
  vector[N] entry = [0, 0, 1, 0, 2, 1, 0, 2]';
  vector[N] x = [0, 1, 0, 1, 0, 1, 0, 1]';
  array[N] int event = {1, 1, 0, 1, 0, 1, 0, 1};
  for (n in 1 : N)
    if (entry[n] >= time[n])
      reject("Entry must precede observed endpoint");
}
parameters {
  real<lower=0> shape;
  vector[2] beta;
}
transformed parameters {
  vector[N] scale = exp(beta[1] + beta[2] * x);
}
model {
  shape ~ lognormal(0, 0.5);
  beta ~ normal(0, 1.5);
  for (n in 1 : N) {
    if (event[n])
      target += weibull_lpdf(time[n] | shape, scale[n]);
    else
      target += weibull_lccdf(time[n] | shape, scale[n]);
    if (entry[n] > 0)
      target += -weibull_lccdf(entry[n] | shape, scale[n]);
  }
}
generated quantities {
  vector[N] log_lik;
  real acceleration_factor = exp(beta[2]);
  real hazard_ratio = exp(-shape * beta[2]);
  real median_control = exp(beta[1]) * pow(log(2), inv(shape));
  real survival_control_at_six = exp(weibull_lccdf(6 | shape, exp(beta[1])));
  for (n in 1 : N) {
    if (event[n])
      log_lik[n] = weibull_lpdf(time[n] | shape, scale[n]);
    else
      log_lik[n] = weibull_lccdf(time[n] | shape, scale[n]);
    if (entry[n] > 0)
      log_lik[n] -= weibull_lccdf(entry[n] | shape, scale[n]);
  }
}
