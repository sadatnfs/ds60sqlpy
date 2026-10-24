#include <cassert>
#include <iostream>
#include <map>

int main() {
  std::map<int, int> counts{{2, 2}, {3, 1}, {4, 1}};
  const auto before = counts.size();
  assert(counts.find(9) == counts.end());
  assert(counts.size() == before);
  assert(counts[9] == 0 && counts.size() == before + 1);
  std::cout << "cpp-035 example 2 checks passed\n";
  return 0;
}
