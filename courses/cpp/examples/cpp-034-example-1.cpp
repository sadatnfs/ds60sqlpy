#include <cassert>
#include <iostream>
#include <vector>

struct Sample {
  int id;
  int value;
};
int main() {
  std::vector<Sample> rows{{1, 10}, {2, 20}, {3, 30}};
  int sum = 0;
  for (const auto &row : rows)
    sum += row.value;
  assert(sum == 60);
  std::cout << "cpp-034 example 1 checks passed\n";
  return 0;
}
