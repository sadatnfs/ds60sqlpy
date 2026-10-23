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
    for(int trial=0;trial<20;++trial){std::atomic<int> count{0};std::promise<void> ready;auto started=ready.get_future();std::thread t([&]{ready.set_value();for(int i=0;i<100;++i)++count;});started.get();for(int i=0;i<100;++i)++count;t.join();assert(count==200);}
    // Reference extension checks for the exercise changes.
    std::atomic<int> baseline{0};assert(baseline.load()==0);
    std::cout << "cpp-033 examples passed\n";
    return 0;
}


// Exercise 1: Identify the schedule point. Name the purpose of the ready handshake. Expected: It proves worker startup, not worker completion.
// Exercise 2: Run bounded stress. Repeat the 200-count scenario 20 times. Expected: 20 exact invariant passes, no sleeps.
// Exercise 3: Add a timeout contract. Wrap the host test process in a finite supervisor deadline. Expected: A deadlock is reported as timeout rather than hanging indefinitely.
// Exercise 4: Repair timing assumptions. Replace a fixed sleep used to infer startup with a promise. Expected: Test proceeds only after the readiness event.
// Exercise 5: Qualify TSan separately. Use an existing supported compiler with -fsanitize=thread on an owned host copy. Expected: Actual build/run receipt or explicit unavailable status.
// Exercise 6: Transfer negative control. Introduce a plain counter race only in a separately instrumented scratch test. Expected: TSan finding expected; production example stays race-free.
