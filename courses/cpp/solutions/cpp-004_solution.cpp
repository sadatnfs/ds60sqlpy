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

int nonnegative_sum(const std::vector<int>& xs) { int total=0; for(int x:xs) { if(x>=0) total+=x; } return total; }
int main() {
    assert(nonnegative_sum({4,-2,0,6})==10);
    assert(nonnegative_sum({})==0);
    assert(nonnegative_sum({-7,-1})==0);
    std::cout << "cpp-004 examples passed\n";
    return 0;
}


// Exercise 1: Trace state. Trace [4,-2,0,6] with a row for each input. Expected: Totals [4,4,4,10], four visits.
// Exercise 2: Change the threshold. Count retained values for >=0 and >0 on [4,-2,0,6]. Expected: Counts 3 and 2; both sums 10.
// Exercise 3: Construct a bounded loop. Sum integers 1 through 4 with an index loop. Expected: 10 from exactly four iterations.
// Exercise 4: Repair a reset. Move total=0 into the loop, predict, then repair the scratch copy. Expected: Broken final total 6; repaired total 10.
// Exercise 5: Test the empty boundary. Run empty and all-negative vectors. Expected: Both totals 0; no element access.
// Exercise 6: Transfer the predicate. Keep readings in [0,5] from [-1,0,4,5,6]. Expected: Values [0,4,5], total 9.
