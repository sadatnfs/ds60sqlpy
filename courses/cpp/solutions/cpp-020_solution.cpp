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

#include <concepts>
template <std::integral T> T identity_sum(T a, T b) { return a + b; }
int main() {
  assert(identity_sum(2, 3) == 5);
  assert(identity_sum(2LL, 3LL) == 5LL);
  static_assert(std::integral<int>);
  static_assert(!std::integral<double>);
  // Reference extension checks for the exercise changes.
  assert(identity_sum(7, 0) == 7);
  assert(identity_sum(7LL, 0LL) == 7LL);
  assert(identity_sum(2LL, 3LL) == 5LL);
  std::cout << "cpp-020 examples passed\n";
  return 0;
}

// Exercise 1: Read deduction. Call identity_sum with int values and long long values. Expected: Result types int and long long respectively.
// Exercise 2: Reject a category. Try identity_sum with two strings in a scratch file. Expected: Constraint-related compile failure.
// Exercise 3: Add a concept. Constrain a function to signed_integral. Expected: int accepted; unsigned rejected.
// Exercise 4: Repair mixed deduction. Call identity_sum(2,3LL), then choose a deliberate common type. Expected: Mixed call fails deduction; explicit long long arguments succeed.
// Exercise 5: Inspect numeric boundary. Explain why INT_MAX+1 is still unsafe for integral T=int. Expected: Concept accepts int but cannot make overflow valid.
// Exercise 6: Transfer a generic test. Run zero-identity tests for int and long long. Expected: sum(x,0)==x for bounded x=7 in both types.
