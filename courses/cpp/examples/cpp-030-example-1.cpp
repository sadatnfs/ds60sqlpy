#include <cassert>
#include <condition_variable>
#include <iostream>
#include <mutex>
#include <queue>
#include <thread>

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
  std::cout << "cpp-030 example 1 checks passed\n";
  return 0;
}
