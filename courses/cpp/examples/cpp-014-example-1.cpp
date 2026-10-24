#include <cassert>
#include <charconv>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

std::optional<int> parse_reading(std::string_view s) {
  int n = 0;
  auto [p, e] = std::from_chars(s.data(), s.data() + s.size(), n);
  if (e != std::errc{} || p != s.data() + s.size() || n < 0)
    return {};
  return n;
}
int main() {
  const std::vector<std::string> rows{"10", "0", "bad", "-2", "25"};
  int accepted = 0, rejected = 0;
  long long total = 0;
  for (const auto &raw : rows) {
    if (auto value = parse_reading(raw)) {
      ++accepted;
      total += *value;
    } else {
      ++rejected;
    }
  }
  assert(accepted == 3 && rejected == 2 && total == 35);
  std::cout << "accepted=" << accepted << " rejected=" << rejected
            << " total=" << total << "\n";
  std::cout << "cpp-014 example 1 checks passed\n";
  return 0;
}
