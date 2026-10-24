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

struct Score {
  int id;
  int points;
};
int main() {
  std::vector<int> xs{-1, 0, 3};
  auto view = xs | std::views::filter([](int x) { return x >= 0; }) |
              std::views::transform([](int x) { return x * 2; });
  std::vector<int> out;
  for (int x : view)
    out.push_back(x);
  assert((out == std::vector<int>{0, 6}));
  std::vector<Score> scores{{1, 9}, {2, 4}};
  std::ranges::sort(scores, {}, &Score::points);
  assert(scores[0].id == 2);
  // Reference extension checks for the exercise changes.
  std::vector<Score> tied{{1, 9}, {3, 4}, {2, 4}};
  std::ranges::sort(tied, [](const Score &a, const Score &b) {
    return std::pair{a.points, a.id} < std::pair{b.points, b.id};
  });
  assert(tied[0].id == 2 && tied[1].id == 3 && tied[2].id == 1);
  std::cout << "cpp-019 examples passed\n";
  return 0;
}

// Exercise 1: Predict lazy output. Filter >=0 then double [-1,0,3]. Expected: [0,6].
// Exercise 2: Change composition. Double first, then filter >0. Expected: [6]; zero is excluded by the new predicate.
// Exercise 3: Materialize ownership. Collect the view into vector<int>. Expected: Stored [0,6] remains independent of later source changes.
// Exercise 4: Repair dangling view. Review a view returned over a local vector. Expected: Reject; keep the owner outside or return a vector.
// Exercise 5: Sort records. Sort scores (id1,9),(id2,4) by points. Expected: ID order [2,1].
// Exercise 6: Transfer stable ties. Add (id3,4) and define deterministic ordering by points then ID. Expected: ID order [2,3,1].
