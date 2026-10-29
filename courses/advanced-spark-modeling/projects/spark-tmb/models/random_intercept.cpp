#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_IVECTOR(group);
  PARAMETER(beta);
  PARAMETER(log_sigma);
  PARAMETER(log_tau);
  PARAMETER_VECTOR(u);
  Type sigma = exp(log_sigma), tau = exp(log_tau), nll = 0;
  for (int g = 0; g < u.size(); ++g)
    nll -= dnorm(u(g), Type(0), tau, true);
  vector<Type> fitted(y.size());
  for (int i = 0; i < y.size(); ++i) {
    fitted(i) = beta + u(group(i));
    nll -= dnorm(y(i), fitted(i), sigma, true);
  }
  ADREPORT(sigma);
  ADREPORT(tau);
  ADREPORT(fitted);
  return nll;
}
