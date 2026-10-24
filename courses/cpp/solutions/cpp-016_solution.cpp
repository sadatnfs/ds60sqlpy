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

struct Batch {
  std::vector<int> values;
  std::string label;
};
int main() {
  Batch a{{1, 2, 3}, "first"};
  Batch copy = a;
  copy.values[0] = 9;
  assert(a.values[0] == 1);
  Batch moved = std::move(a);
  assert((moved.values == std::vector<int>{1, 2, 3}));
  a = Batch{{4}, "reused"};
  assert(a.values[0] == 4);
  // Reference extension checks for the exercise changes.
  auto make_batch = []() { return Batch{{8, 9}, "factory"}; };
  auto returned = make_batch();
  assert((returned.values == std::vector<int>{8, 9}));
  std::cout << "cpp-016 examples passed\n";
  return 0;
}

// Exercise 1: Contrast copy and move. Copy a Batch and mutate the copy. Expected: Original values unchanged.
// Exercise 2: Inspect the receiver. Move Batch([1,2,3]) into a new owner. Expected: Receiver values exactly [1,2,3].
// Exercise 3: Reuse the source. Assign Batch([4]) to the moved-from source. Expected: Source is safely usable with value [4].
// Exercise 4: Repair an invalid assumption. Remove a test requiring every moved-from vector to be empty. Expected: Test verifies receiver and source validity only.
// Exercise 5: Keep rule of zero. List special members needed for Batch. Expected: No custom destructor/copy/move needed.
// Exercise 6: Transfer to return values. Return Batch from a factory and store it. Expected: Correct owned vector after factory scope ends.
