// SPDX-License-Identifier: MIT
// Original correlated random-intercept/slope model, integrated by TMB Laplace.
#include <TMB.hpp>

template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(x);
  DATA_VECTOR(y);
  DATA_IVECTOR(group);
  PARAMETER_VECTOR(beta);
  PARAMETER_VECTOR(log_sd);
  PARAMETER(correlation_coordinate);
  PARAMETER_MATRIX(z);
  Type sigma = exp(log_sd(0));
  Type tau0 = exp(log_sd(1));
  Type tau1 = exp(log_sd(2));
  Type rho = tanh(correlation_coordinate);
  matrix<Type> effects(z.rows(), 2);
  Type loss = Type(0);
  for (int g = 0; g < z.rows(); ++g) {
    loss -= dnorm(z(g, 0), Type(0), Type(1), true);
    loss -= dnorm(z(g, 1), Type(0), Type(1), true);
    effects(g, 0) = tau0 * z(g, 0);
    effects(g, 1) =
        tau1 * (rho * z(g, 0) + sqrt(Type(1) - rho * rho) * z(g, 1));
  }
  vector<Type> fitted(y.size());
  for (int i = 0; i < y.size(); ++i) {
    fitted(i) = beta(0) + beta(1) * x(i) + effects(group(i), 0) +
                effects(group(i), 1) * x(i);
    loss -= dnorm(y(i), fitted(i), sigma, true);
  }
  REPORT(fitted);
  REPORT(effects);
  ADREPORT(beta);
  ADREPORT(rho);
  return loss;
}
