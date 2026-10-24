#include <cassert>
#include <iostream>

int twice(int x) { return x * 2; }
int main() {
  int evaluations = 0;
  assert(++evaluations == 1);
#ifdef NDEBUG
  if (evaluations != 0)
    return 1;
  std::cout << "assert removed: evaluations=0\n";
#else
  if (evaluations != 1)
    return 1;
  std::cout << "assert active: evaluations=1\n";
#endif
  std::cout << "cpp-013 example 2 checks passed\n";
  return 0;
}
