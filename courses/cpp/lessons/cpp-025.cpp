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

int checked_at(const std::vector<int> &xs, std::size_t i) { return xs.at(i); }
int main() {
  assert(checked_at({2, 4}, 1) == 4);
  bool rejected = false;
  try {
    checked_at({2, 4}, 2);
  } catch (const std::out_of_range &) {
    rejected = true;
  }
  assert(rejected);
  std::cout << "cpp-025 examples passed\n";
  return 0;
}

// Exercise 1: Classify the defect. Explain index 2 into vector size 2. Expected: Out of bounds; valid indices 0 and 1.
// Exercise 2: Use checked access. Compare at(2) with the contract of operator[2]. Expected: at throws; unchecked invalid access is undefined behavior.
// Exercise 3: Prepare instrumented build. Compile the safe reference with sanitizer flags on a supported host. Expected: Compile/link/run statuses and compiler version recorded.
// Exercise 4: Diagnose a controlled failure. In a separate instrumented scratch program introduce one heap out-of-bounds access. Expected: Nonzero sanitizer report naming access and source location; never claim ordinary profile detection.
// Exercise 5: Repair and rerun. Replace invalid access with a valid index or explicit check. Expected: Sanitizer report disappears on that test path; result is correct.
// Exercise 6: Transfer signed arithmetic. Review INT_MAX+1 and use pre-add range validation. Expected: Input rejected before overflow.
