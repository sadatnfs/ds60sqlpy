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

long long serial_total(std::span<const int> xs){return std::accumulate(xs.begin(),xs.end(),0LL);}
struct Analysis {
    long long total=0;
    std::size_t accepted=0,rejected=0,completed=0,cancelled=0,failed_tasks=0;
    bool failed=false;
};
std::optional<int> parse_bounded(std::string_view text) {
    if(text.empty() || text.size()>16) return {};
    int value=0;
    auto [end,error]=std::from_chars(text.data(),text.data()+text.size(),value);
    if(error!=std::errc{} || end!=text.data()+text.size() || value<0) return {};
    return value;
}
Analysis analyze(const std::vector<std::string>& input,bool inject_failure=false) {
    if(input.size()>100) throw std::invalid_argument("row budget exceeded");
    Analysis result;
    std::vector<int> values;
    for(const auto& raw:input) {
        if(auto value=parse_bounded(raw)) values.push_back(*value);
        else ++result.rejected;
    }
    result.accepted=values.size();
    long long totals[2]{0,0};
    std::size_t completed[2]{0,0},failed[2]{0,0};
    std::atomic<bool> stop{false};
    auto worker=[&](std::size_t slot) {
        for(std::size_t i=slot;i<values.size();i+=2) {
            if(stop.load()) break;
            if(inject_failure && i==0) {
                ++failed[slot]; stop.store(true); break;
            }
            totals[slot]+=values[i]; ++completed[slot];
        }
    };
    // Fixed two workers; bounded input is the admission queue for this capstone.
    std::thread first(worker,0);
    try {
        std::thread second(worker,1);
        first.join(); second.join();
    } catch(...) {
        stop.store(true);
        if(first.joinable()) first.join();
        throw;
    }
    result.completed=completed[0]+completed[1];
    result.failed_tasks=failed[0]+failed[1];
    result.cancelled=result.accepted-result.completed-result.failed_tasks;
    result.failed=result.failed_tasks!=0;
    // A failed product deliberately publishes no partial total.
    if(!result.failed) result.total=totals[0]+totals[1];
    return result;
}
int main() {
    const std::vector<int> rows{1,2,3,4,5,6};long long first=0,second=0;
    std::thread a([&]{first=serial_total(std::span<const int>(rows).first(3));});std::thread b([&]{second=serial_total(std::span<const int>(rows).subspan(3));});a.join();b.join();assert(first==6 && second==15 && first+second==serial_total(rows));
    assert(serial_total(std::span<const int>{})==0);
    const std::vector<std::string> raw{"1","2","3","4","5","6","bad","3x"};
    const auto success=analyze(raw);
    assert(success.accepted==6 && success.rejected==2 && success.completed==6);
    assert(success.total==21 && !success.failed && success.cancelled==0);
    const auto failure=analyze(raw,true);
    assert(failure.failed && failure.failed_tasks==1 && failure.total==0);
    assert(failure.completed+failure.cancelled+failure.failed_tasks==failure.accepted);
    const auto empty=analyze({});
    assert(empty.total==0 && empty.accepted==0 && !empty.failed);
    bool budget_rejected=false;
    try { analyze(std::vector<std::string>(101,"1")); }
    catch(const std::invalid_argument&) { budget_rejected=true; }
    assert(budget_rejected);
    // Reference extension checks for the exercise changes.
    const std::vector<int> uneven{1,2,3,4,5};auto split=std::span<const int>(uneven);assert(serial_total(split.first(2))+serial_total(split.subspan(2))==15);
    std::cout << "cpp-042 examples passed\n";
    return 0;
}


// Exercise 1: Define budgets. Declare at most 2 workers, 100 input rows and 16 characters per integer field. Expected: Three limits plus rejection behavior documented.
// Exercise 2: Prove serial parity. Compare two-worker total on [1,2,3,4,5,6] with serial oracle. Expected: Subtotals 6 and 15; total 21.
// Exercise 3: Account for bad rows. Add strings bad and 3x through the strict parser. Expected: Six accepted, two rejected, accepted total 21.
// Exercise 4: Inject worker failure. Make one partition report an error before publication. Expected: No successful combined report; error and completed/cancelled work accounted.
// Exercise 5: Test empty and uneven work. Check zero rows and five rows [1,2,3,4,5]. Expected: Totals 0 and 15 with no lost tail.
// Exercise 6: Deliver reviewer packet. Include source, fixtures, serial oracle, failure test, build/run receipts and limits. Expected: A second learner reproduces normal, empty, invalid and failure cases.
