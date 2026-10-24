#include <cassert>
#include <iostream>
#include <ranges>
#include <vector>

struct Score {
  int id;
  int points;
};
int main() {
  std::vector<int> xs{-1, 0, 3};
  auto view = xs | std::views::filter([](int x) { return x >= 0; });
  std::vector<int> observed;
  for (int value : view)
    observed.push_back(value);
  assert((observed == std::vector<int>{0, 3}));
  std::cout << "cpp-019 example 1 checks passed\n";
  return 0;
}
