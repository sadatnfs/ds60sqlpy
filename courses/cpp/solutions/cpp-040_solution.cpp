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

bool safe_id(std::string_view s){if(s.empty()||s.size()>16)return false;for(unsigned char c:s)if(!((c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'))return false;return true;}
int main() {
    assert(safe_id("batch_7"));assert(!safe_id("../secret"));assert(!safe_id("a/b"));assert(!safe_id(""));assert(!safe_id(std::string(17,'a')));
    // Reference extension checks for the exercise changes.
    assert(safe_id("0"));assert(safe_id(std::string(16,'a')));assert(!safe_id("a\\b"));assert(!safe_id("Upper"));
    std::cout << "cpp-040 examples passed\n";
    return 0;
}


// Exercise 1: Write the grammar. Specify accepted identifier characters and length. Expected: 1 to 16 lowercase ASCII letters, digits or underscore.
// Exercise 2: Test normal input. Validate batch_7 and 0. Expected: Both accepted.
// Exercise 3: Reject traversal shapes. Test ../secret, a/b and a backslash-separated path. Expected: All rejected before filesystem access.
// Exercise 4: Repair overclaim. Explain why this is not a general symlink-safe path sandbox. Expected: No claim of arbitrary path containment; scope remains identifiers.
// Exercise 5: Enforce size. Test empty, 16-character and 17-character strings. Expected: Reject, accept, reject.
// Exercise 6: Transfer row budgets. Set max 100 rows and 256 bytes per row before parsing a file. Expected: Oversized input rejected with counts and no partial publication.
