#include <cassert>
#include <iostream>

int add(int, int);

int add(int a, int b) { return a + b; }
int main() {
  assert(add(0, 0) == 0);
  std::cout << "zero inputs link and run too\n";
  std::cout << "cpp-012 example 2 checks passed\n";
  return 0;
}
