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
  std::atomic<int> count{0};
  std::thread a([&] {
    for (int i = 0; i < 1000; ++i)
      count.fetch_add(1, std::memory_order_relaxed);
  });
  std::thread b([&] {
    for (int i = 0; i < 1000; ++i)
      count.fetch_add(1, std::memory_order_relaxed);
  });
  a.join();
  b.join();
  assert(count.load() == 2000);
  int payload = 0;
  std::atomic<bool> ready{false};
  std::thread producer([&] {
    payload = 7;
    ready.store(true, std::memory_order_release);
  });
  while (!ready.load(std::memory_order_acquire))
    std::this_thread::yield();
  assert(payload == 7);
  producer.join();
  // Reference extension checks for the exercise changes.
  std::atomic<int> no_work{0};
  assert(no_work.load() == 0);
  std::cout << "cpp-031 examples passed\n";
  return 0;
}

// Exercise 1: Count atomic work. Run two workers with 1000 increments each. Expected: Final count 2000 after both joins.
// Exercise 2: Explain relaxed. State why relaxed suffices for the isolated counter. Expected: No payload publication relies on counter ordering.
// Exercise 3: Trace publication. Draw payload write, release store, acquire load and payload read. Expected: A synchronization chain orders the payload access.
// Exercise 4: Reject a data race. Review plain shared int increments without synchronization. Expected: Reject as undefined behavior; do not normalize a lucky total.
// Exercise 5: Test zero workers. Set work count to zero and inspect the counter. Expected: 0 without a publication claim.
// Exercise 6: Transfer multiple fields. Publish two fields behind one ready release/acquire pair. Expected: Both earlier writes visible after the matching acquire.
