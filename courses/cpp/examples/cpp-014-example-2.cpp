#include <cassert>
#include <charconv>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>

std::optional<int> parse_reading(std::string_view s) {
  int n = 0;
  auto [p, e] = std::from_chars(s.data(), s.data() + s.size(), n);
  if (e != std::errc{} || p != s.data() + s.size() || n < 0)
    return {};
  return n;
}
int main() {
  assert(parse_reading("0") == 0);
  assert(!parse_reading("10x"));
  std::cout << "cpp-014 example 2 checks passed\n";
  return 0;
}
