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

int twice(int x) { return x * 2; }
int main() {
  if (twice(3) != 6 || twice(0) != 0)
    return 1;
  std::cout << "2 always-active checks\n";
  // Reference extension checks for the exercise changes.
  if (twice(7) != 14 || twice(-2) != -4)
    return 1;
  std::cout << "cpp-013 examples passed\n";
  return 0;
}

// Exercise 1: Read flags. Explain -std=c++20, -Wall, -Wextra and -Wpedantic. Expected: Language selection and three diagnostic groups distinguished.
// Exercise 2: Run named tests. Use the supplied CMake project and ctest --output-on-failure. Expected: One or more registered tests actually execute; record count and status.
// Exercise 3: Create a failing check. Change the expected twice(3) result to 7 in a scratch copy. Expected: Executable exit 1 and failing test.
// Exercise 4: Repair a disabled test. Build a scratch assert-only test with -DNDEBUG. Expected: The wrong assert disappears; an if-based test still fails.
// Exercise 5: Test zero. Keep the always-active twice(0)==0 check. Expected: Exit 0 for the correct function.
// Exercise 6: Transfer a regression. Break twice to x+x+1, run both tests, then restore. Expected: Both normal and zero contracts reject the broken function.
