#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_VECTOR(x);
  DATA_VECTOR(x_prediction);
  DATA_INTEGER(prediction_mode);
  PARAMETER_VECTOR(beta);
  PARAMETER(log_sigma);
  if (beta.size() != 2)
    error("This prepared model has an intercept and one slope");
  if (prediction_mode == 1) {
    vector<Type> prediction(x_prediction.size());
    for (int i = 0; i < x_prediction.size(); ++i)
      prediction(i) = beta(0) + beta(1) * x_prediction(i);
    REPORT(prediction);
    return Type(0);
  }
  if (prediction_mode != 0 || x.size() != y.size())
    error("Invalid prepared regression data");
  Type nll = 0;
  for (int i = 0; i < y.size(); ++i)
    nll -= dnorm(y(i), beta(0) + beta(1) * x(i), exp(log_sigma), true);
  return nll;
}
