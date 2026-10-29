#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_VECTOR(time);
  DATA_VECTOR(entry);
  DATA_IVECTOR(event);
  PARAMETER(log_scale);
  PARAMETER(log_shape);
  Type scale = exp(log_scale), shape = exp(log_shape), nll = 0;
  for (int i = 0; i < time.size(); ++i) {
    Type cumulative = pow(time(i) / scale, shape);
    Type entry_cumulative = Type(0);
    if (entry(i) > Type(0))
      entry_cumulative = pow(entry(i) / scale, shape);
    Type log_hazard =
        log_shape - log_scale + (shape - Type(1)) * (log(time(i)) - log_scale);
    nll += cumulative - entry_cumulative - Type(event(i)) * log_hazard;
  }
  ADREPORT(scale);
  ADREPORT(shape);
  return nll;
}
