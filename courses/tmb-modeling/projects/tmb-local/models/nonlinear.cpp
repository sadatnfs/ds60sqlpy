#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_VECTOR(time);
  DATA_VECTOR(time_pred);
  PARAMETER(log_a);
  PARAMETER(log_b);
  PARAMETER(offset);
  PARAMETER(log_sigma);
  Type a = exp(log_a), b = exp(log_b), sigma = exp(log_sigma);
  vector<Type> mean(y.size()), prediction(time_pred.size());
  Type nll = 0;
  for (int i = 0; i < y.size(); ++i) {
    mean(i) = a * exp(-b * time(i)) + offset;
    nll -= dnorm(y(i), mean(i), sigma, true);
  }
  for (int j = 0; j < time_pred.size(); ++j)
    prediction(j) = a * exp(-b * time_pred(j)) + offset;
  REPORT(mean);
  ADREPORT(a);
  ADREPORT(b);
  ADREPORT(prediction);
  return nll;
}
