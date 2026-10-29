#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  DATA_INTEGER(mode);
  DATA_MATRIX(covariance);
  DATA_SPARSE_MATRIX(precision);
  DATA_VECTOR(scales);
  PARAMETER_VECTOR(state);
  if (mode == 0)
    return density::MVNORM(covariance)(state);
  if (mode == 1)
    return density::GMRF(precision)(state);
  if (mode == 2)
    return density::VECSCALE(density::MVNORM(covariance), scales)(state);
  if (mode == 3)
    return density::SCALE(density::MVNORM(covariance), scales(0))(state);
  error("Unknown fixed density comparison mode");
  return Type(0);
}
