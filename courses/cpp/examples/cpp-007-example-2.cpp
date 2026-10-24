#include <cassert>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
  std::vector<int> xs;
  xs.reserve(4);
  assert(xs.size() == 0 && xs.capacity() >= 4);
  assert(xs.begin() == xs.end());
  assert(std::accumulate(xs.begin(), xs.end(), 0LL) == 0);
  xs.push_back(8);
  const auto index = std::size_t{0};
  xs.reserve(xs.capacity() + 1);
  // Any old element pointer or iterator is invalid after this reallocation.
  assert(xs[index] == 8);
  std::cout << "size=" << xs.size() << " value=" << xs[index] << "\n";
  std::cout << "cpp-007 example 2 checks passed\n";
  return 0;
}
