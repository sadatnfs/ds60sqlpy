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

constexpr int release_schema=1;
int main() {
    static_assert(release_schema==1);std::vector<int> fixture{1,2,3};if(std::accumulate(fixture.begin(),fixture.end(),0)!=6)return 1;std::cout << "schema=1 rows=3 total=6\n";
    std::cout << "cpp-041 examples passed\n";
    return 0;
}


// Exercise 1: Inventory the release. Record source revision or content hashes plus compiler/architecture. Expected: All identities present without machine-specific source paths.
// Exercise 2: Compare build modes. Run always-active checks in Debug and Release host builds. Expected: Both report rows=3,total=6 and actual executed test count.
// Exercise 3: Bound a benchmark. Declare row count, repeats and output checksum before timing. Expected: Units, variability and same-work evidence retained.
// Exercise 4: Repair platform claims. Review a packet tested only on arm64 Linux but claiming Windows. Expected: Windows remains unqualified until actual execution.
// Exercise 5: Check offline replay. Rebuild in a fresh owned directory using prepared dependencies. Expected: No network access needed and tests reproduce.
// Exercise 6: Transfer rollback. Keep a previous known-good binary and compatible input contract. Expected: A reviewer can identify rollback artifact and acceptance test.
