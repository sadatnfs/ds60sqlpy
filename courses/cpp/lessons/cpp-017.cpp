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

struct ParseError { std::string reason; };
using Result=std::variant<int,ParseError>;
Result positive(int x) { if(x<0)return ParseError{"negative"}; return x; }
int main() {
    auto ok=positive(0); assert(std::get<int>(ok)==0);
    auto bad=positive(-1); assert(std::get<ParseError>(bad).reason=="negative");
    std::optional<int> missing; assert(!missing);
    std::cout << "cpp-017 examples passed\n";
    return 0;
}


// Exercise 1: Classify alternatives. Evaluate positive for 0,5,-1. Expected: Two success values 0,5 and one negative error.
// Exercise 2: Write an observer. Use get_if to print value or reason without throwing. Expected: All three inputs produce a classified outcome.
// Exercise 3: Preserve a missing value. Distinguish optional<int>{0} from nullopt. Expected: First present, second absent.
// Exercise 4: Repair bad access. Call get<int> on the error in a scratch copy. Expected: bad_variant_access; replace with checked dispatch.
// Exercise 5: Choose a boundary. Explain why a missing required file is fatal while one bad row can be recorded. Expected: Separate process-level error from row-level rejection.
// Exercise 6: Transfer richer reasons. Add too_large for values above 100. Expected: 101 maps to too_large, -1 to negative, 100 succeeds.
