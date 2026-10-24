#include <cassert>
#include <future>
#include <iostream>
#include <thread>

int main() {
  std::promise<void> ready;
  auto started = ready.get_future();
  int result = 0;
  std::thread worker([&] {
    result = 42;
    ready.set_value();
  });
  started.get();
  assert(result == 42);
  worker.join();
  std::cout << "cpp-033 example 1 checks passed\n";
  return 0;
}
