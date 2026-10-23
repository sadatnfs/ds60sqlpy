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

struct Sample { int id; int value; };
int main() {
    std::vector<Sample> rows{{1,10},{2,20},{3,30}};std::vector<int> values;values.reserve(rows.size());for(const auto& r:rows)values.push_back(r.value);
    int aos=0;for(const auto& r:rows)aos+=r.value;int soa=std::accumulate(values.begin(),values.end(),0);assert(aos==60&&soa==60);assert(values.size()==3);
    // Reference extension checks for the exercise changes.
    std::vector<int> reserved;reserved.reserve(100);assert(reserved.size()==0&&reserved.capacity()>=100);
    std::cout << "cpp-034 examples passed\n";
    return 0;
}


// Exercise 1: Draw both layouts. Sketch three records as AoS and as separate ID/value vectors. Expected: Same three logical rows with different physical grouping.
// Exercise 2: Prove result equality. Sum values in both representations. Expected: 60 from each.
// Exercise 3: Inspect reserve. Reserve 100 on an empty vector, then inspect size. Expected: Size 0; capacity at least 100.
// Exercise 4: Repair an unfair comparison. One candidate omits the value 30. Expected: Reject timing comparison until both checksums equal 60.
// Exercise 5: Measure bounded work. Repeat one-field summation with a fixed row cap and build mode. Expected: Same checksum, duration units and repetitions recorded.
// Exercise 6: Transfer the workload. Now request ID and value together for every row. Expected: Reassess the locality hypothesis without assuming SoA always wins.
