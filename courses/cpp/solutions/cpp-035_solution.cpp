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
    std::vector<int> values{2,3,2,4};std::map<int,int> counts;for(int x:values)++counts[x];assert(counts[2]==2);assert(counts[3]==1);assert(std::count(values.begin(),values.end(),2)==counts[2]);
    assert(counts.find(9)==counts.end());
    // Reference extension checks for the exercise changes.
    const auto keys_before=counts.size();assert(counts.find(9)==counts.end());assert(counts.size()==keys_before);std::map<int,int> empty;assert(empty.find(2)==empty.end());
    std::cout << "cpp-035 examples passed\n";
    return 0;
}


// Exercise 1: Count linear work. Search four rows for key 2 once. Expected: Four comparisons and count 2.
// Exercise 2: Build an index. Build frequency map for [2,3,2,4]. Expected: Three keys with counts 2,1,1.
// Exercise 3: Compare repeated queries. Compare 100 full scans with one index build plus 100 lookups. Expected: Same answers; setup and lookup work reported separately.
// Exercise 4: Repair mutating lookup. Use counts[9] to inspect absence, then repair with find. Expected: operator[] inserts zero; find leaves key count unchanged.
// Exercise 5: Check empty data. Build and query an empty frequency index. Expected: No key 2 and zero matching rows.
// Exercise 6: Transfer sorted storage. Compare binary search on a sorted vector with map lookup. Expected: Sorting cost, duplicate range and lookup budget documented.
