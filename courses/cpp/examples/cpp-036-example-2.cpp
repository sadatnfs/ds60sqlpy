#include <cassert>
#include <iostream>

constexpr int square(int x) { return x * x; }
consteval int fixed_limit() { return 16; }
int main() {
  int runtime = 5;
  assert(square(runtime) == 25);
  std::cout << "cpp-036 example 2 checks passed\n";
  return 0;
}
