#include <cassert>
#include <iostream>
#include <string>
#include <string_view>

int main() {
  std::string text = "alpha";
  std::string_view prefix(text.data(), 2);
  assert(prefix == "al");
  text[0] = 'A';
  assert(prefix == "Al");
  std::cout << "cpp-018 example 2 checks passed\n";
  return 0;
}
