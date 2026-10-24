#include <algorithm>
#include <cassert>
#include <iostream>
#include <stdexcept>

int clamp_reading(int x, int low, int high) {
  if (low > high)
    throw std::invalid_argument("reversed bounds");
  return std::max(low, std::min(x, high));
}
int main() {
  assert(clamp_reading(12, 0, 10) == 10);
  std::cout << "cpp-005 example 1 checks passed\n";
  return 0;
}
