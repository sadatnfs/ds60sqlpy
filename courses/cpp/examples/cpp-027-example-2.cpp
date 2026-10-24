#include <cassert>
#include <iostream>

namespace vendored {
constexpr int api_version = 1;
constexpr int add(int a, int b) { return a + b; }
} // namespace vendored
int main() {
  assert(vendored::add(2, 3) == 5);
  std::cout << "cpp-027 example 2 checks passed\n";
  return 0;
}
