#include <TMB.hpp>
template <class Type> Type objective_function<Type>::operator()() {
  PARAMETER(x);
  Type positive = CppAD::CondExpGt(x, Type(0), x, Type(0));
  return positive * positive;
}
