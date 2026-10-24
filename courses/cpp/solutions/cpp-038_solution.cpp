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

std::optional<int> safe_add(int a, int b) {
  if (a < 0 || b < 0 || a > std::numeric_limits<int>::max() - b)
    return {};
  return a + b;
}
int main() {
  assert(safe_add(100, 25) == 125);
  assert(!safe_add(std::numeric_limits<int>::max(), 1));
  double value = 0.1 + 0.2;
  assert(std::abs(value - 0.3) < 1e-12);
  assert(100 + 25 == 125);
  // Reference extension checks for the exercise changes.
  assert(safe_add(0, 0) == 0);
  assert(!safe_add(-1, 2));
  assert(safe_add(std::numeric_limits<int>::max(), 0) ==
         std::numeric_limits<int>::max());
  std::cout << "cpp-038 examples passed\n";
  return 0;
}

// Exercise 1: Keep exact units. Add 100 and 25 integer cents. Expected: Exactly 125 cents.
// Exercise 2: Reject overflow. Try INT_MAX plus 1. Expected: Absent result without evaluating overflow.
// Exercise 3: Inspect rounding. Print 0.1+0.2 with sufficient precision. Expected: Possible difference from 0.3 is recorded with a suitable tolerance.
// Exercise 4: Repair one-size tolerance. Explain why epsilon=0.1 is poor for both tiny and huge measurements. Expected: A scale-aware absolute/relative policy stated.
// Exercise 5: Check zero boundary. Run safe_add(0,0) and safe_add(-1,2). Expected: Present 0 and rejected negative input.
// Exercise 6: Transfer stability. Compare sums [1e16,1,-1e16] under different groupings. Expected: Floating sums can differ; exact expected mathematical total is 1.
