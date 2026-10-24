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

std::optional<int> parse_int(std::string_view s) {
  int out = 0;
  auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), out);
  if (ec != std::errc{} || ptr != s.data() + s.size())
    return std::nullopt;
  return out;
}
int main() {
  assert(parse_int("42") == 42);
  assert(parse_int("-7") == -7);
  assert(parse_int("0") == 0);
  assert(!parse_int("12x"));
  assert(!parse_int(""));
  assert(!parse_int("999999999999999999999"));
  std::cout << "cpp-006 examples passed\n";
  return 0;
}

// Exercise 1: Trace consumption. Parse 42 and 12x and inspect pointer distance. Expected: 42 consumes 2; 12x consumes 2 of 3 and is rejected.
// Exercise 2: Retain zero. Parse 0 and -7 through optional<int>. Expected: Both are present values.
// Exercise 3: Build a ledger. Classify [12,12x,empty,0] as raw strings. Expected: Two accepted values [12,0], two rejected records.
// Exercise 4: Repair prefix acceptance. Change the condition to check only ec in a scratch copy. Expected: 12x is incorrectly accepted until ptr==end is restored.
// Exercise 5: Reject overflow. Parse 21 decimal nines. Expected: Absent result with out-of-range conversion, never a wrapped integer.
// Exercise 6: Define whitespace policy. Compare literal space-42-space with a deliberately trimmed copy. Expected: Strict parser rejects original; explicit trim accepts 42.
