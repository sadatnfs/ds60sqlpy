#include <cassert>
#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <vector>

int checked_at(const std::vector<int> &xs, std::size_t i) { return xs.at(i); }
int main() {
  bool caught = false;
  try {
    (void)checked_at({2, 4}, 2);
  } catch (const std::out_of_range &) {
    caught = true;
  }
  assert(caught);
  std::cout << "cpp-025 example 2 checks passed\n";
  return 0;
}
