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

constexpr int square(int x){return x*x;}
consteval int fixed_limit(){return 16;}
int main() {
    static_assert(square(4)==16);static_assert(fixed_limit()==16);
    int runtime=5;assert(square(runtime)==25);
    // Reference extension checks for the exercise changes.
    constexpr int squares[]{0,1,4,9,16};static_assert(squares[4]==16);static_assert(square(0)==0);
    std::cout << "cpp-036 examples passed\n";
    return 0;
}


// Exercise 1: Distinguish phases. Classify static_assert(square(4)==16) and square(runtime). Expected: First compile-time requirement; second runtime-capable call.
// Exercise 2: Add a lookup table. Build squares for indices 0 through 4 with constexpr data. Expected: [0,1,4,9,16].
// Exercise 3: Force constant evaluation. Create a consteval limit function and call with constant input. Expected: Build succeeds with a constant result.
// Exercise 4: Diagnose runtime argument. Pass an input read at runtime to a consteval function. Expected: Compilation fails; use constexpr when runtime calls are needed.
// Exercise 5: Check a numeric boundary. Limit table inputs so multiplication cannot overflow int. Expected: Declared bound and safe result range documented.
// Exercise 6: Transfer build budget. Compare bounded table sizes 16 and 256 in an owned host build. Expected: Record compile duration and artifact size without asserting a universal ratio.
