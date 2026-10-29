#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  PARAMETER(mu);
  PARAMETER(log_sigma);
  Type sigma = exp(log_sigma);
  parallel_accumulator<Type> total(this);
  for (int row = 0; row < y.size(); ++row) {
    Type standardized = (y(row) - mu) / sigma;
    total += log_sigma + Type(0.5) * standardized * standardized +
             Type(0.5) * log(Type(2) * Type(M_PI));
  }
  return total;
}
