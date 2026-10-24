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

int checked_square(int x){if(x<0)throw std::invalid_argument("negative task");return x*x;}
int main() {
    auto first=std::async(std::launch::async,checked_square,3);auto second=std::async(std::launch::async,checked_square,4);assert(first.get()+second.get()==25);
    auto failed=std::async(std::launch::async,checked_square,-1);bool seen=false;try{failed.get();}catch(const std::invalid_argument&){seen=true;}assert(seen);
    std::cout << "cpp-032 examples passed\n";
    return 0;
}


// Exercise 1: Set a budget. Define maximum workers 2 and queued tasks 4. Expected: Both bounds documented independently.
// Exercise 2: Compare serial results. Square 3 and 4 serially and in two futures. Expected: Exact total 25 in both paths.
// Exercise 3: Propagate a failure. Include task -1 and call get. Expected: invalid_argument reaches the owner.
// Exercise 4: Repair fire-and-forget. Review discarded futures and missing result accounting. Expected: Observe every result or exception and join owned work.
// Exercise 5: Test empty workload. Run no tasks through the serial/reference contract. Expected: Empty results and total 0.
// Exercise 6: Transfer backpressure. Sketch a capacity-4 queue for ten tasks and two consumers. Expected: At most 2 running plus 4 queued, remaining producer work blocked.
