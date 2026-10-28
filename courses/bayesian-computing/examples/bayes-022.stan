transformed data {
  int N = 10;
  vector[N] y = [-2.5, -2, -1.8, -1.7, -2.1, 1.5, 1.8, 2.2, 2.4, 2]';
}
parameters {
  ordered[2] mu;
  real<lower=0> sigma;
  real<lower=0, upper=1> mixture_weight;
}
model {
  mu[1] ~ normal(-2, 1);
  mu[2] ~ normal(2, 1);
  sigma ~ normal(0, 1);
  mixture_weight ~ beta(2, 2);
  for (n in 1 : N) {
    target += log_mix(mixture_weight, normal_lpdf(y[n] | mu[1], sigma),
                      normal_lpdf(y[n] | mu[2], sigma));
  }
}
generated quantities {
  vector[N] log_lik;
  vector[N] responsibility_first;
  vector[N] y_rep;
  for (n in 1 : N) {
    real first = normal_lpdf(y[n] | mu[1], sigma);
    real second = normal_lpdf(y[n] | mu[2], sigma);
    log_lik[n] = log_mix(mixture_weight, first, second);
    responsibility_first[n] = exp(log(mixture_weight) + first - log_lik[n]);
    if (bernoulli_rng(mixture_weight))
      y_rep[n] = normal_rng(mu[1], sigma);
    else
      y_rep[n] = normal_rng(mu[2], sigma);
  }
}
