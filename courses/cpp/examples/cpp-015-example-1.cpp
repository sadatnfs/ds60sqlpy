#include <cassert>
#include <iostream>
#include <memory>
#include <utility>

struct Tracked {
  int *live;
  explicit Tracked(int &count) : live(&count) { ++*live; }
  ~Tracked() { --*live; }
  Tracked(const Tracked &) = delete;
  Tracked &operator=(const Tracked &) = delete;
};
int main() {
  auto p = std::make_unique<int>(7);
  auto q = std::move(p);
  assert(!p && q && *q == 7);
  std::cout << "cpp-015 example 1 checks passed\n";
  return 0;
}
