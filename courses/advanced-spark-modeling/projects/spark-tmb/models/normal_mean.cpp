#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  PARAMETER(mu);
  PARAMETER(log_sigma);
  Type sigma = exp(log_sigma);
  Type nll = 0;
  vector<Type> residual(y.size());
  for (int i = 0; i < y.size(); ++i) {
    residual(i) = y(i) - mu;
    nll -= dnorm(y(i), mu, sigma, true);
  }
  REPORT(residual);
  ADREPORT(sigma);
  SIMULATE {
    for (int i = 0; i < y.size(); ++i)
      y(i) = rnorm(mu, sigma);
    REPORT(y);
  }
  return nll;
}
