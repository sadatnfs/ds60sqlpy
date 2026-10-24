#include <cassert>
#include <iostream>

int add(int, int);

int add(int a, int b) { return a + b; }
int main() {
  assert(add(2, 3) == 5);
  std::cout << "declaration and definition linked\n";
  std::cout << "cpp-012 example 1 checks passed\n";
  return 0;
}
