#include <cassert>
#include <iostream>
#include <string>
#include <variant>

struct ParseError {
  std::string reason;
};

using Result = std::variant<int, ParseError>;

Result positive(int x) {
  if (x < 0)
    return ParseError{"negative"};
  return x;
}
int main() {
  auto result = positive(-1);
  assert(std::get<ParseError>(result).reason == "negative");
  std::cout << "cpp-017 example 2 checks passed\n";
  return 0;
}
