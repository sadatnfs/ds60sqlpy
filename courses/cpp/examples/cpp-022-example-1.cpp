#include <cassert>
#include <iostream>
#include <string>

std::string encode(int id, int cents) {
  return "v1," + std::to_string(id) + "," + std::to_string(cents);
}
int main() {
  assert(encode(7, 125) == "v1,7,125");
  std::cout << "cpp-022 example 1 checks passed\n";
  return 0;
}
