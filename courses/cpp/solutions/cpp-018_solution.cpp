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

int sum_view(std::span<const int> xs) { return std::accumulate(xs.begin(),xs.end(),0); }
int main() {
    std::vector<int> values{2,4,6}; std::span<const int> view(values); assert(sum_view(view)==12); assert(sum_view(view.subspan(1,2))==10);
    assert(sum_view(std::span<const int>{})==0);
    std::string owned="alpha"; std::string_view prefix(owned.data(),2); assert(prefix=="al");
    // Reference extension checks for the exercise changes.
    auto slice_ok=[](std::size_t size,std::size_t offset,std::size_t count){return offset<=size && count<=size-offset;};assert(!slice_ok(3,2,2));assert(slice_ok(3,1,2));assert(slice_ok(0,0,0));
    std::cout << "cpp-018 examples passed\n";
    return 0;
}


// Exercise 1: Identify ownership. Draw vector storage and its span. Expected: One owner and one non-owning view.
// Exercise 2: Select a subrange. Sum the final two values of [2,4,6]. Expected: 10 with original vector unchanged.
// Exercise 3: Write a bounds guard. Validate offset=2,count=2 for size=3 before subspan. Expected: Reject because only one value remains.
// Exercise 4: Repair invalidation. Review span created before vector growth that reallocates. Expected: Recreate span after growth; never dereference stale span.
// Exercise 5: Test empty view. Pass an empty span to sum_view. Expected: 0 without dereference.
// Exercise 6: Transfer lifetime reasoning. Review string_view returned from a local string. Expected: Reject; return string ownership or borrow caller-owned text.
