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

struct Tracked {
  int *live;
  explicit Tracked(int &count) : live(&count) { ++*live; }
  ~Tracked() { --*live; }
  Tracked(const Tracked &) = delete;
  Tracked &operator=(const Tracked &) = delete;
};
int main() {
  int live = 0;
  {
    auto owner = std::make_unique<Tracked>(live);
    assert(live == 1);
    auto next = std::move(owner);
    assert(!owner && next);
  }
  assert(live == 0);
  try {
    auto owner = std::make_unique<Tracked>(live);
    throw std::runtime_error("abort");
  } catch (const std::runtime_error &) {
  }
  assert(live == 0);
  // Reference extension checks for the exercise changes.
  {
    std::vector<std::unique_ptr<Tracked>> owners;
    for (int i = 0; i < 3; ++i)
      owners.push_back(std::make_unique<Tracked>(live));
    assert(live == 3);
  }
  assert(live == 0);
  std::cout << "cpp-015 examples passed\n";
  return 0;
}

// Exercise 1: Trace ownership. Draw p and q before and after moving unique_ptr<int>(7). Expected: One live allocation; exactly one owner at each point.
// Exercise 2: Check normal cleanup. Run the Tracked scoped case. Expected: live=1 inside and 0 afterward.
// Exercise 3: Check exceptional cleanup. Throw after constructing Tracked and catch outside. Expected: live=0 after catch.
// Exercise 4: Reject accidental copy. Try auto q=p with unique_ptr. Expected: Compile failure; move only when ownership should change.
// Exercise 5: Handle empty owner. Default-construct unique_ptr<int> and inspect Boolean state. Expected: false, with no dereference.
// Exercise 6: Transfer to a collection. Own three unique_ptr<int> values in a vector then leave scope. Expected: All three allocations released; no manual delete loop.
