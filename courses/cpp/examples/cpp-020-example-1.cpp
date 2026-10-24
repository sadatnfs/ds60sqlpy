#include <cassert>
#include <concepts>
#include <iostream>

#include <concepts>
template <std::integral T> T identity_sum(T a, T b) { return a + b; }
int main() {
  assert(identity_sum(2, 3) == 5);
  std::cout << "cpp-020 example 1 checks passed\n";
  return 0;
}
