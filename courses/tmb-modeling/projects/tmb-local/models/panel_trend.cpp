#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_VECTOR(time);
  DATA_IVECTOR(group);
  DATA_VECTOR(time_pred);
  DATA_IVECTOR(group_pred);
  PARAMETER(log_a);
  PARAMETER(log_b);
  PARAMETER(offset);
  PARAMETER(log_sigma);
  PARAMETER(log_tau);
  PARAMETER_VECTOR(u);
  Type a = exp(log_a), b = exp(log_b), sigma = exp(log_sigma),
       tau = exp(log_tau), nll = 0;
  for (int g = 0; g < u.size(); ++g)
    nll -= dnorm(u(g), Type(0), tau, true);
  for (int i = 0; i < y.size(); ++i) {
    Type mean = a * exp(-b * time(i)) + offset + u(group(i));
    nll -= dnorm(y(i), mean, sigma, true);
  }
  vector<Type> prediction(time_pred.size());
  for (int i = 0; i < time_pred.size(); ++i)
    prediction(i) = a * exp(-b * time_pred(i)) + offset + u(group_pred(i));
  ADREPORT(prediction);
  ADREPORT(sigma);
  ADREPORT(tau);
  return nll;
}
