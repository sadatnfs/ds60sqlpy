#include <cassert>
#include <iostream>
#include <string>
#include <vector>

struct Batch {
  std::vector<int> values;
  std::string label;
};
int main() {
  Batch a{{1, 2}, "A"};
  Batch b = a;
  b.values[0] = 9;
  assert((a.values == std::vector<int>{1, 2}));
  assert((b.values == std::vector<int>{9, 2}));
  std::cout << "cpp-016 example 1 checks passed\n";
  return 0;
}
