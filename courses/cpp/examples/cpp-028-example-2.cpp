#include <cassert>
#include <charconv>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>

struct Record {
  int id;
  int cents;
};

std::optional<Record> parse_record(std::string_view s) {
  auto cut = s.find(',');
  if (cut == s.npos)
    return {};
  int id = 0, cents = 0;
  auto [p, e] = std::from_chars(s.data(), s.data() + cut, id);
  auto [q, f] = std::from_chars(s.data() + cut + 1, s.data() + s.size(), cents);
  if (e != std::errc{} || f != std::errc{} || p != s.data() + cut ||
      q != s.data() + s.size() || id < 0 || cents < 0)
    return {};
  return Record{id, cents};
}
int main() {
  assert(!parse_record("7,125x"));
  std::cout << "cpp-028 example 2 checks passed\n";
  return 0;
}
