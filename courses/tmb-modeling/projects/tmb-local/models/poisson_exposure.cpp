#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  DATA_VECTOR(x);
  DATA_VECTOR(exposure);
  PARAMETER(alpha);
  PARAMETER(beta);
  Type nll = 0;
  vector<Type> expected(y.size());
  for (int i = 0; i < y.size(); ++i) {
    expected(i) = exposure(i) * exp(alpha + beta * x(i));
    nll -= dpois(y(i), expected(i), true);
  }
  ADREPORT(expected);
  return nll;
}
