#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  PARAMETER_ARRAY(state);
  PARAMETER(phi_row_raw);
  PARAMETER(phi_col_raw);
  PARAMETER(log_scale);
  Type phi_row = tanh(phi_row_raw), phi_col = tanh(phi_col_raw);
  return density::SCALE(
      density::SEPARABLE(density::AR1(phi_col), density::AR1(phi_row)),
      exp(log_scale))(state);
}
