#include <algorithm>
#include <atomic>
#include <cassert>
#include <charconv>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <future>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <numeric>
#include <optional>
#include <queue>
#include <ranges>
#include <span>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>
#include <variant>
#include <vector>

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
  auto good = parse_record("7,125");
  assert(good && good->id == 7 && good->cents == 125);
  assert(!parse_record("7,125x"));
  assert(!parse_record("7,-1"));
  assert(parse_record("0,0"));
  // Reference extension checks for the exercise changes.
  std::vector<std::string> corpus{"7,125", "0,0", "7,125x", "7,-1"};
  int accepted = 0, rejected = 0;
  for (const auto &raw : corpus) {
    if (parse_record(raw))
      ++accepted;
    else
      ++rejected;
  }
  assert(accepted == 2 && rejected == 2);
  std::optional<Record> retained;
  {
    std::string temporary = "8,250";
    retained = parse_record(temporary);
  }
  assert(retained && retained->cents == 250);
  std::cout << "cpp-028 examples passed\n";
  return 0;
}

// Exercise 1: Write public contracts. Document parse_record input grammar and result ownership. Expected: Two nonnegative integer fields, full consumption, owned success.
// Exercise 2: Build independent fixture. Use [7,125;0,0;7,125x;7,-1] as four records. Expected: Two accepted and two rejected.
// Exercise 3: Package a consumer. Split header, implementation and CLI into the host project. Expected: Separate library and executable targets build and link.
// Exercise 4: Inject a regression. Remove the full-consumption check in a scratch implementation. Expected: 7,125x must fail the golden test.
// Exercise 5: Check boundary ownership. Return a parsed record after input string goes out of scope. Expected: Record fields remain valid copied integers.
// Exercise 6: Deliver compatibility evidence. Run a consumer against current public header and library. Expected: Compiler/platform identity, test output and source inventory retained.
