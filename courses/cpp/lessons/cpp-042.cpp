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

long long serial_total(std::span<const int> xs) {
  return std::accumulate(xs.begin(), xs.end(), 0LL);
}
int main() {
  const std::vector<int> rows{1, 2, 3, 4, 5, 6};
  long long first = 0, second = 0;
  std::thread a(
      [&] { first = serial_total(std::span<const int>(rows).first(3)); });
  std::thread b(
      [&] { second = serial_total(std::span<const int>(rows).subspan(3)); });
  a.join();
  b.join();
  assert(first == 6 && second == 15 && first + second == serial_total(rows));
  assert(serial_total(std::span<const int>{}) == 0);
  std::cout << "cpp-042 examples passed\n";
  return 0;
}

// Exercise 1: Define budgets. Declare at most 2 workers, 100 input rows and 16 characters per integer field. Expected: Three limits plus rejection behavior documented.
// Exercise 2: Prove serial parity. Compare two-worker total on [1,2,3,4,5,6] with serial oracle. Expected: Subtotals 6 and 15; total 21.
// Exercise 3: Account for bad rows. Add strings bad and 3x through the strict parser. Expected: Six accepted, two rejected, accepted total 21.
// Exercise 4: Inject worker failure. Make one partition report an error before publication. Expected: No successful combined report; error and completed/cancelled work accounted.
// Exercise 5: Test empty and uneven work. Check zero rows and five rows [1,2,3,4,5]. Expected: Totals 0 and 15 with no lost tail.
// Exercise 6: Deliver reviewer packet. Include source, fixtures, serial oracle, failure test, build/run receipts and limits. Expected: A second learner reproduces normal, empty, invalid and failure cases.
