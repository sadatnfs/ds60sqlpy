#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_INTEGER(prediction_mode);
  DATA_INTEGER(n_prediction);
  PARAMETER(mu);
  PARAMETER(log_sigma);
  if (prediction_mode == 1) {
    if (n_prediction < 1 || n_prediction > 4096)
      error("Prediction row count is outside the prepared contract");
    vector<Type> prediction(n_prediction);
    prediction.setConstant(mu);
    REPORT(prediction);
    return Type(0);
  }
  if (prediction_mode != 0)
    error("Unknown prepared operation");
  Type nll = 0;
  for (int i = 0; i < y.size(); ++i)
    nll -= dnorm(y(i), mu, exp(log_sigma), true);
  return nll;
}
