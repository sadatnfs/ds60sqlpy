// SPDX-License-Identifier: MIT
// Original exact Gaussian panel covariance, not a copy or port of AFModel.
#include <TMB.hpp>
#include <vector>

template <class Type> Type objective_function<Type>::operator()() {
  DATA_MATRIX(X);
  DATA_VECTOR(y);
  DATA_IVECTOR(group);
  DATA_IVECTOR(time);
  DATA_INTEGER(groups);
  DATA_SCALAR(time_scale);
  PARAMETER_VECTOR(beta);
  PARAMETER(log_sigma);
  PARAMETER_VECTOR(log_tau);
  PARAMETER(phi_coordinate);
  PARAMETER(scale_trend);
  Type sigma = exp(log_sigma);
  Type tau0 = exp(log_tau(0));
  Type tau1 = exp(log_tau(1));
  Type phi = tanh(phi_coordinate);
  vector<Type> fitted = X * beta;
  Type loss = Type(0);
  for (int g = 0; g < groups; ++g) {
    std::vector<int> rows;
    for (int i = 0; i < y.size(); ++i)
      if (group(i) == g)
        rows.push_back(i);
    int n = rows.size();
    vector<Type> residual(n);
    matrix<Type> covariance(n, n);
    for (int i = 0; i < n; ++i) {
      int a = rows[i];
      Type ta = Type(time(a)) / time_scale;
      Type sa = sigma * exp(scale_trend * ta);
      residual(i) = y(a) - fitted(a);
      for (int j = 0; j < n; ++j) {
        int b = rows[j];
        Type tb = Type(time(b)) / time_scale;
        Type sb = sigma * exp(scale_trend * tb);
        int lag = std::abs(time(a) - time(b));
        Type correlation = Type(1);
        for (int k = 0; k < lag; ++k)
          correlation *= phi;
        covariance(i, j) =
            tau0 * tau0 + tau1 * tau1 * ta * tb + sa * sb * correlation;
      }
    }
    loss += density::MVNORM_t<Type>(covariance)(residual);
  }
  REPORT(fitted);
  ADREPORT(beta);
  ADREPORT(phi);
  ADREPORT(sigma);
  return loss;
}
