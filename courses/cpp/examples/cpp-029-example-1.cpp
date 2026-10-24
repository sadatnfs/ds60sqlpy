#include <cassert>
#include <iostream>
#include <thread>

int main() {
  int answer = 0;
  std::thread t([&] { answer = 42; });
  t.join();
  assert(answer == 42);
  std::cout << "cpp-029 example 1 checks passed\n";
  return 0;
}
