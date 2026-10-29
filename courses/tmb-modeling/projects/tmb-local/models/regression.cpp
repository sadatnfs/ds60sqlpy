#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_MATRIX(X);
  DATA_MATRIX(X_pred);
  PARAMETER_VECTOR(beta);
  PARAMETER(log_sigma);
  Type sigma = exp(log_sigma);
  vector<Type> mean = X * beta;
  vector<Type> prediction = X_pred * beta;
  Type nll = 0;
  for (int i = 0; i < y.size(); ++i)
    nll -= dnorm(y(i), mean(i), sigma, true);
  REPORT(mean);
  ADREPORT(prediction);
  ADREPORT(sigma);
  return nll;
}
