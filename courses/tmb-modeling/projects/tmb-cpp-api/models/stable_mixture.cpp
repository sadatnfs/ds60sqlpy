#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(y);
  PARAMETER(eta);
  PARAMETER(mu_one);
  PARAMETER(mu_two);
  PARAMETER(log_sigma);
  Type log_p = -logspace_add(Type(0), -eta);
  Type log_other = -logspace_add(Type(0), eta);
  Type total = 0;
  for (int i = 0; i < y.size(); ++i) {
    Type first = dnorm(y(i), mu_one, exp(log_sigma), true);
    Type second = dnorm(y(i), mu_two, exp(log_sigma), true);
    total -= logspace_add(log_p + first, log_other + second);
  }
  return total;
}
