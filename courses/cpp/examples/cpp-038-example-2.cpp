#include <cassert>
#include <cmath>
#include <iostream>

int main() {
  assert(std::abs((0.1 + 0.2) - 0.3) < 1e-12);
  std::cout << "cpp-038 example 2 checks passed\n";
  return 0;
}
