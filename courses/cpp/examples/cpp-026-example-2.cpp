#include <cassert>
#include <iostream>
#include <numeric>
#include <vector>

int total(const std::vector<int> &xs) {
  return std::accumulate(xs.begin(), xs.end(), 0);
}
int main() {
  long long checksum = 0;
  for (int i = 0; i < 1000; ++i)
    checksum += total({2, 4, 6});
  assert(checksum == 12000);
  std::cout << "checksum=" << checksum << "\n";
  std::cout << "cpp-026 example 2 checks passed\n";
  return 0;
}
