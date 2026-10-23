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

std::vector<int> reversed(std::vector<int> xs){std::reverse(xs.begin(),xs.end());return xs;}
int main() {
    assert((reversed({1,2,3})==std::vector<int>{3,2,1}));
    for(int a=-2;a<=2;++a)for(int b=-2;b<=2;++b){std::vector<int> xs{a,b};assert(reversed(reversed(xs))==xs);}
    assert(reversed({}).empty());
    std::cout << "cpp-024 examples passed\n";
    return 0;
}


// Exercise 1: Write a golden case. Reverse [1,2,3] against a literal expected vector. Expected: [3,2,1].
// Exercise 2: Enumerate a property. Test all pairs from integers -2 through 2. Expected: 25 cases satisfy double reversal.
// Exercise 3: Add a boundary corpus. Include empty, singleton and duplicate vectors. Expected: [], [7], [2,2] preserved after double reversal.
// Exercise 4: Expose a weak property. Replace reversal with identity in a scratch copy. Expected: Double-reverse property passes but golden reversal fails.
// Exercise 5: Save a reproduction. Break reversal to drop the first item. Expected: Small failing vector and exact observed output retained.
// Exercise 6: Transfer to a parser. Design encode/decode properties and independent malformed inputs. Expected: Round-trip valid records; reject suffix junk and wrong versions.
