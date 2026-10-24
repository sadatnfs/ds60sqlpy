#include <cassert>
#include <iostream>
#include <limits>

extern "C" int add_checked(int a, int b, int *out) noexcept {
  if (!out)
    return 1;
  if ((b > 0 && a > std::numeric_limits<int>::max() - b) ||
      (b < 0 && a < std::numeric_limits<int>::min() - b))
    return 2;
  *out = a + b;
  return 0;
}
int main() {
  assert(add_checked(2, 3, nullptr) == 1);
  std::cout << "cpp-023 example 2 checks passed\n";
  return 0;
}
