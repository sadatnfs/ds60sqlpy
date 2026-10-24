#include <atomic>
#include <cassert>
#include <future>
#include <iostream>
#include <thread>

int main() {
  for (int trial = 0; trial < 20; ++trial) {
    std::atomic<int> count{0};
    std::promise<void> ready;
    auto started = ready.get_future();
    std::thread t([&] {
      ready.set_value();
      for (int i = 0; i < 100; ++i)
        ++count;
    });
    started.get();
    for (int i = 0; i < 100; ++i)
      ++count;
    t.join();
    assert(count == 200);
  }
  std::cout << "cpp-033 example 2 checks passed\n";
  return 0;
}
