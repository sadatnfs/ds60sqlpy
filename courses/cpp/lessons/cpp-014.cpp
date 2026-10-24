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

std::optional<int> parse_reading(std::string_view s) { int n=0;auto [p,e]=std::from_chars(s.data(),s.data()+s.size(),n);if(e!=std::errc{}||p!=s.data()+s.size()||n<0)return {};return n; }
int main() {
    std::vector<std::string> rows{"10","0","bad","-2","25"}; int accepted=0,rejected=0,total=0;
    for(const auto& row:rows) { if(auto n=parse_reading(row)) {++accepted;total+=*n;} else ++rejected; }
    assert(accepted==3 && rejected==2 && total==35);
    assert(accepted+rejected==static_cast<int>(rows.size()));
    std::cout << "cpp-014 examples passed\n";
    return 0;
}


// Exercise 1: Define the input contract. Write the grammar and rejection policy for the five rows. Expected: Nonnegative base-10 whole fields; bad and -2 rejected.
// Exercise 2: Implement the ledger. Store raw row, accepted value or rejection reason. Expected: 5 ledger entries, 3 accepted, 2 rejected.
// Exercise 3: Produce the report. Calculate accepted count and exact total. Expected: accepted=3 rejected=2 total=35.
// Exercise 4: Inject trailing junk. Replace 25 with 25x. Expected: accepted=2 rejected=3 total=10.
// Exercise 5: Test empty input. Run no rows through the same pipeline. Expected: 0 accepted, 0 rejected, total 0.
// Exercise 6: Hand off reproducibility. Package source, fixture, commands, test results and limitations. Expected: Reviewer reproduces the 5-row ledger and failed suffix case.
