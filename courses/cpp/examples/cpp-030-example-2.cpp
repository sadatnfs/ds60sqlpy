#include <cassert>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <queue>

int main() {
  std::mutex mutex;
  std::condition_variable cv;
  std::queue<int> queue;
  bool closed = true;
  std::unique_lock<std::mutex> lock(mutex);
  cv.wait(lock, [&] { return !queue.empty() || closed; });
  assert(queue.empty() && closed);
  std::cout << "cpp-030 example 2 checks passed\n";
  return 0;
}
