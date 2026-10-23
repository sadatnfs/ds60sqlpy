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

int total(const std::vector<int>& xs){return std::accumulate(xs.begin(),xs.end(),0);}
int main() {
    assert(total({2,4,6})==12);
    auto start=std::chrono::steady_clock::now(); long long checksum=0;for(int i=0;i<1000;++i)checksum+=total({2,4,6});auto end=std::chrono::steady_clock::now();assert(checksum==12000);std::cout << "elapsed_ns=" << std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count() << "\n";
    // Reference extension checks for the exercise changes.
    assert(total({})==0);assert(total({-1,0,1})==0);
    std::cout << "cpp-026 examples passed\n";
    return 0;
}


// Exercise 1: Reproduce first. Write the expected sum of [2,4,6]. Expected: 12 from three values.
// Exercise 2: Inspect a stack. Use an already available debugger on a -g host build and break in total. Expected: Call stack includes main and total; xs has three values.
// Exercise 3: Measure a bounded workload. Run 1000 totals and record steady_clock duration. Expected: Checksum 12000 and nonnegative measured duration with units.
// Exercise 4: Reject a false benchmark. Explain why one observed faster run proves little. Expected: Build mode, workload, repetitions and variability listed.
// Exercise 5: Test an empty case. Inspect total({}) with debugger or assertions. Expected: 0 and no element access.
// Exercise 6: Transfer a hypothesis. Replace a linear scan with a map lookup and state a measurable hypothesis. Expected: Same exact results, operation counts and bounded measurements compared.
