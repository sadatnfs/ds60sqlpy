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

template <std::ranges::input_range R> std::vector<int> keep_positive(R &&xs) {
  std::vector<int> out;
  for (auto x : xs)
    if (x > 0)
      out.push_back(x);
  return out;
}
int main() {
  auto out = keep_positive(std::vector<int>{-1, 0, 2, 2});
  assert((out == std::vector<int>{2, 2}));
  assert(keep_positive(std::vector<int>{}).empty());
  std::cout << "cpp-037 examples passed\n";
  return 0;
}

// Exercise 1: State range requirements. Explain why one pass is sufficient for keep_positive. Expected: Input-range traversal only, no size prepass.
// Exercise 2: Preserve multiplicity. Filter [-1,0,2,2] with >0. Expected: [2,2].
// Exercise 3: Retain ownership. Call with a temporary vector and use result afterward. Expected: Result remains valid and owns its elements.
// Exercise 4: Repair two-pass design. Review counting an input_range then traversing it again. Expected: Use one pass or require forward_range with justification.
// Exercise 5: Check empty input. Use an empty vector and an empty span. Expected: Both yield empty vectors.
// Exercise 6: Transfer a projection. Filter records by their points while retaining complete records. Expected: Output retains IDs, values and duplicate qualifying rows.
