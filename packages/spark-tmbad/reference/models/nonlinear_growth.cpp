// SPDX-License-Identifier: MIT
// Original nonlinear growth model with a Gaussian random effect on log amplitude.
#include <TMB.hpp>

template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(time);
  DATA_VECTOR(y);
  DATA_IVECTOR(group);
  PARAMETER_VECTOR(theta);
  PARAMETER_VECTOR(u);
  Type sigma = exp(theta(3));
  Type tau = exp(theta(4));
  Type rate = exp(theta(2));
  Type loss = Type(0);
  for (int g = 0; g < u.size(); ++g)
    loss -= dnorm(u(g), Type(0), tau, true);
  vector<Type> fitted(y.size());
  for (int i = 0; i < y.size(); ++i) {
    fitted(i) = theta(0) +
                exp(theta(1) + u(group(i))) * (Type(1) - exp(-rate * time(i)));
    loss -= dnorm(y(i), fitted(i), sigma, true);
  }
  REPORT(fitted);
  REPORT(u);
  ADREPORT(theta);
  return loss;
}
