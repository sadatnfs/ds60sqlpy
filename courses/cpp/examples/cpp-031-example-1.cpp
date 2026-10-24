#include <atomic>
#include <cassert>
#include <iostream>
#include <thread>

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
  std::cout << "cpp-031 example 1 checks passed\n";
  return 0;
}
