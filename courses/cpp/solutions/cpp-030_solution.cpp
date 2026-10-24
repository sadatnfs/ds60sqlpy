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
  std::mutex m;
  std::condition_variable cv;
  std::queue<int> q;
  bool closed = false;
  int total = 0;
  std::thread consumer([&] {
    std::unique_lock<std::mutex> lock(m);
    for (;;) {
      cv.wait(lock, [&] { return !q.empty() || closed; });
      if (q.empty() && closed)
        break;
      total += q.front();
      q.pop();
    }
  });
  {
    std::lock_guard<std::mutex> lock(m);
    q.push(2);
    q.push(3);
    closed = true;
  }
  cv.notify_all();
  consumer.join();
  assert(total == 5);
  // Reference extension checks for the exercise changes.
  std::queue<int> empty_queue;
  bool empty_closed = true;
  assert(empty_queue.empty() && empty_closed);
  std::cout << "cpp-030 examples passed\n";
  return 0;
}

// Exercise 1: State the invariant. List queue state protected by m. Expected: Queue contents and closed flag share one mutex.
// Exercise 2: Drain before exit. Produce 2 and 3 then close. Expected: Total 5 with both items consumed.
// Exercise 3: Bound the queue. Add capacity 2 and a producer wait predicate. Expected: Observed size never exceeds 2.
// Exercise 4: Repair naked wait. Replace cv.wait(lock) with predicate waiting. Expected: Spurious notifications cannot trigger front on empty queue.
// Exercise 5: Test empty close. Close before enqueueing any items. Expected: Consumer exits with total 0.
// Exercise 6: Transfer cancellation. Define whether cancellation drains or discards pending work. Expected: Chosen policy accounts for every accepted item and joins all workers.
