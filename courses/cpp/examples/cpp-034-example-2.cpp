#include <cassert>
#include <iostream>
#include <numeric>
#include <vector>

struct Sample {
  int id;
  int value;
};
int main() {
  std::vector<int> values{10, 20, 30};
  assert(std::accumulate(values.begin(), values.end(), 0) == 60);
  std::cout << "cpp-034 example 2 checks passed\n";
  return 0;
}
