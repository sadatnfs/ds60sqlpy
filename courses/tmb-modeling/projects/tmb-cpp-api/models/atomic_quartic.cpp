#include <TMB.hpp>
TMB_ATOMIC_VECTOR_FUNCTION(original_quartic, 1,
                           ty[0] = tx[0] * tx[0] * tx[0] * tx[0];
                           , px[0] = Type(4) * tx[0] * tx[0] * tx[0] * py[0];)
template <class Type> Type objective_function<Type>::operator()() {
  PARAMETER(x);
  CppAD::vector<Type> input(1);
  input[0] = x;
  return original_quartic(input)[0] + Type(0.5) * x * x;
}
