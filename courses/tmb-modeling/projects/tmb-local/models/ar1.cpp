#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_INTEGER(horizon);
  PARAMETER(beta);
  PARAMETER(log_sigma);
  PARAMETER(log_tau);
  PARAMETER(phi_raw);
  PARAMETER_VECTOR(u);
  Type sigma = exp(log_sigma), tau = exp(log_tau), phi = tanh(phi_raw);
  Type nll = density::SCALE(density::AR1(phi), tau)(u);
  for (int i = 0; i < y.size(); ++i)
    nll -= dnorm(y(i), beta + u(i), sigma, true);
  vector<Type> prediction(horizon), innovation_variance(horizon);
  for (int h = 0; h < horizon; ++h) {
    Type persistence = pow(phi, h + 1);
    prediction(h) = beta + persistence * u(u.size() - 1);
    innovation_variance(h) =
        tau * tau * (Type(1) - persistence * persistence) + sigma * sigma;
  }
  ADREPORT(phi);
  ADREPORT(prediction);
  REPORT(innovation_variance);
  return nll;
}
