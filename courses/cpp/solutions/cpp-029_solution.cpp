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
  int result = 0;
  std::thread worker([&result] { result = 42; });
  worker.join();
  assert(result == 42);
  std::atomic<bool> stop{false};
  std::promise<void> ready;
  auto started = ready.get_future();
  std::thread cancellable([&] {
    ready.set_value();
    while (!stop.load())
      std::this_thread::yield();
  });
  started.get();
  stop.store(true);
  cancellable.join();
  assert(stop.load());
  // Reference extension checks for the exercise changes.
  int next_result = 0;
  {
    auto task = std::async(std::launch::async, [] { return 7; });
    next_result = task.get();
  }
  assert(next_result == 7);
  std::cout << "cpp-029 examples passed\n";
  return 0;
}

// Exercise 1: Trace lifetimes. Draw result, worker creation, write, join and scope exit. Expected: The owner remains alive until after join.
// Exercise 2: Read after joining. Compute 42 on one worker and read afterward. Expected: 42, with a documented join before access.
// Exercise 3: Request cancellation. Run the supplied ready handshake then set stop and join. Expected: Worker terminates without a sleep-based timing assumption.
// Exercise 4: Repair detach. Review detaching a worker that captures a local by reference. Expected: Reject detached borrow; keep ownership until join.
// Exercise 5: Translate to jthread. On a qualified C++20 library use jthread and stop_token. Expected: request_stop followed by scope exit joins; record compiler/library support.
// Exercise 6: Transfer failure cleanup. Add an owner-side early return and keep joining mandatory. Expected: No joinable thread reaches destructor; no dangling capture.
