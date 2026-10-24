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

int main() {
  std::vector<int> original{3, 1, 3, 0};
  auto sorted = original;
  std::sort(sorted.begin(), sorted.end());
  assert((sorted == std::vector<int>{0, 1, 3, 3}));
  assert(original[0] == 3);
  assert(std::accumulate(sorted.begin(), sorted.end(), 0LL) == 7);
  assert(std::count(sorted.begin(), sorted.end(), 3) == 2);
  std::cout << "cpp-007 examples passed\n";
  return 0;
}

// Exercise 1: Predict sorting. Sort [3,1,3,0] on paper. Expected: [0,1,3,3], size 4.
// Exercise 2: Preserve evidence. Sort a copy and compare the original. Expected: Original remains [3,1,3,0].
// Exercise 3: Count a boundary. Use count_if to count >=3. Expected: 2 matching elements.
// Exercise 4: Repair a wrong total. Replace accumulate start 0LL with 10LL, then repair. Expected: Wrong total 17; correct total 7.
// Exercise 5: Check an empty vector. Sort, count and sum an empty vector. Expected: Size 0, count 0, sum 0; no dereference.
// Exercise 6: Transfer to ordered unique values. Sort [3,1,3,0], then erase the unique tail. Expected: [0,1,3], size 3.
