#include <cassert>
#include <iostream>

namespace vendored {
constexpr int api_version = 1;
constexpr int add(int a, int b) { return a + b; }
} // namespace vendored
int main() {
  static_assert(vendored::api_version == 1);
  std::cout << "cpp-027 example 1 checks passed\n";
  return 0;
}
