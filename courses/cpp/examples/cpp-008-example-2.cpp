#include <cassert>
#include <iostream>
#include <vector>

int main() {
  const std::vector<int> xs{2, 4};
  auto ys = xs;
  ys[0] = 99;
  assert((xs == std::vector<int>{2, 4}));
  assert((ys == std::vector<int>{99, 4}));
  std::cout << "cpp-008 example 2 checks passed\n";
  return 0;
}
