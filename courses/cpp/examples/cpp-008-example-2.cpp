#include <iostream>
#include <vector>

std::vector<int> doubled(const std::vector<int> &xs) {
  auto out = xs;
  for (int &x : out)
    x *= 2;
  return out;
}
int main() {
  const std::vector<int> xs{2, 4};
  auto ys = xs;
  ys[0] = 99;
  std::cout << "cpp-008 example 2 checks passed\n";
  return 0;
}
