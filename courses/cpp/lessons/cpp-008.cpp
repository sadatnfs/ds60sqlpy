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

std::vector<int> doubled(const std::vector<int> &xs) {
  auto out = xs;
  for (int &x : out)
    x *= 2;
  return out;
}
int main() {
  const std::vector<int> input{2, 4};
  auto output = doubled(input);
  assert((output == std::vector<int>{4, 8}));
  assert((input == std::vector<int>{2, 4}));
  output[0] = 99;
  assert(input[0] == 2);
  assert(doubled({}).empty());
  std::cout << "cpp-008 examples passed\n";
  return 0;
}

// Exercise 1: Draw owners. Draw input, copied output and borrowed parameter. Expected: Two owners and one temporary borrow, no extra owner for the reference.
// Exercise 2: Predict mutation. Change output[0] to 99 after doubled([2,4]). Expected: Input first value 2; output first value 99.
// Exercise 3: Write a const observer. Write size_of(const vector<int>&) without mutation. Expected: [2,4] gives 2; empty gives 0.
// Exercise 4: Diagnose const assignment. Attempt xs[0]=9 through const vector<int>& in a scratch file. Expected: Compilation fails; remove mutation to repair.
// Exercise 5: Identify a lifetime bug. Review a function returning const vector<int>& to its local result. Expected: Reject the reference return; return vector<int> by value.
// Exercise 6: Transfer a safe result. Call doubled with temporary [5] and retain the result. Expected: Stored result remains [10] after the full expression.
