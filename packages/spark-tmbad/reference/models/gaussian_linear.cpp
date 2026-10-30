// SPDX-License-Identifier: MIT
// Original reference template. TMB and linked dependencies retain their own licenses.
#include <TMB.hpp>

template <class Type> Type objective_function<Type>::operator()() {
  DATA_MATRIX(X);
  DATA_VECTOR(y);
  DATA_VECTOR(prior_center);
  DATA_VECTOR(prior_precision);
  PARAMETER_VECTOR(beta);
  PARAMETER(log_sigma);
  Type sigma = exp(log_sigma);
  vector<Type> fitted = X * beta;
  Type loss = Type(0);
  for (int i = 0; i < y.size(); ++i)
    loss -= dnorm(y(i), fitted(i), sigma, true);
  for (int j = 0; j < beta.size(); ++j) {
    if (asDouble(prior_precision(j)) > 0)
      loss -= dnorm(beta(j), prior_center(j),
                    Type(1) / sqrt(prior_precision(j)), true);
  }
  REPORT(fitted);
  ADREPORT(beta);
  ADREPORT(sigma);
  return loss;
}
