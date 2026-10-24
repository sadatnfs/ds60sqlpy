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

extern "C" int add_checked(int a, int b, int *out) noexcept {
  if (!out)
    return 1;
  if ((b > 0 && a > std::numeric_limits<int>::max() - b) ||
      (b < 0 && a < std::numeric_limits<int>::min() - b))
    return 2;
  *out = a + b;
  return 0;
}
int main() {
  int out = 0;
  assert(add_checked(2, 3, &out) == 0 && out == 5);
  assert(add_checked(2, 3, nullptr) == 1);
  assert(add_checked(std::numeric_limits<int>::max(), 1, &out) == 2);
  std::cout << "cpp-023 examples passed\n";
  return 0;
}

// Exercise 1: Separate interfaces. List the add_checked source contract and binary assumptions. Expected: Names/types/statuses versus compiler/platform/linkage distinguished.
// Exercise 2: Call a valid boundary. Pass 2,3 and a writable output integer. Expected: Status 0 and output 5.
// Exercise 3: Reject null output. Pass nullptr for out. Expected: Status 1, no invalid access.
// Exercise 4: Repair exception leakage. Review a C wrapper that lets std::runtime_error escape. Expected: Catch inside wrapper and map to a documented status.
// Exercise 5: Check overflow. Call INT_MAX plus 1. Expected: Status 2; no overflowing addition.
// Exercise 6: Transfer a shared library. Build the wrapper separately in an owned host project and record compiler/architecture. Expected: Real link/load receipt plus matching header, no inferred portability.
