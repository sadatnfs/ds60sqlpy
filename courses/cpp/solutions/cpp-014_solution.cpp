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
struct Ledger { int accepted=0; int rejected=0; long long total=0; };
Ledger report_rows(const std::vector<std::string>& rows) {
    Ledger report;
    for (const auto& row: rows) {
        if (auto value=parse_reading(row)) { ++report.accepted; report.total+=*value; }
        else { ++report.rejected; }
    }
    return report;
}
int main(int argc, char** argv) {
    if (argc != 1) {
        if (argc != 3 || std::string_view(argv[1]) != "--input") {
            std::cerr << "usage: analyzer --input FILE\n";
            return 2;
        }
        std::ifstream input(argv[2]);
        if (!input) { std::cerr << "cannot open input file\n"; return 2; }
        std::vector<std::string> file_rows;
        std::string line;
        char character=0;
        while (input.get(character)) {
            if (character == '\n') {
                if (file_rows.size() >= 100) { std::cerr << "input budget exceeded\n"; return 2; }
                file_rows.push_back(line);
                line.clear();
            } else {
                if (line.size() >= 32) { std::cerr << "input budget exceeded\n"; return 2; }
                line.push_back(character);
            }
        }
        if (!line.empty()) {
            if (file_rows.size() >= 100) { std::cerr << "input budget exceeded\n"; return 2; }
            file_rows.push_back(line);
        }
        if (input.bad()) { std::cerr << "input read failure\n"; return 2; }
        const auto report=report_rows(file_rows);
        std::cout << "accepted=" << report.accepted << " rejected=" << report.rejected
                  << " total=" << report.total << '\n';
        return 0;
    }
    std::vector<std::string> rows{"10","0","bad","-2","25"}; int accepted=0,rejected=0,total=0;
    for(const auto& row:rows) { if(auto n=parse_reading(row)) {++accepted;total+=*n;} else ++rejected; }
    assert(accepted==3 && rejected==2 && total==35);
    assert(accepted+rejected==static_cast<int>(rows.size()));
    // Reference extension checks for the exercise changes.
    int a2=0,r2=0,t2=0;for(std::string_view raw:{"10","0","bad","-2","25x"}){if(auto value=parse_reading(raw)){++a2;t2+=*value;}else ++r2;}assert(a2==2&&r2==3&&t2==10);
    std::cout << "cpp-014 examples passed\n";
    return 0;
}


// Exercise 1: Define the input contract. Write the grammar and rejection policy for the five rows. Expected: Nonnegative base-10 whole fields; bad and -2 rejected.
// Exercise 2: Implement the ledger. Store raw row, accepted value or rejection reason. Expected: 5 ledger entries, 3 accepted, 2 rejected.
// Exercise 3: Produce the report. Calculate accepted count and exact total. Expected: accepted=3 rejected=2 total=35.
// Exercise 4: Inject trailing junk. Replace 25 with 25x. Expected: accepted=2 rejected=3 total=10.
// Exercise 5: Test empty input. Run no rows through the same pipeline. Expected: 0 accepted, 0 rejected, total 0.
// Exercise 6: Hand off reproducibility. Package source, fixture, commands, test results and limitations. Expected: Reviewer reproduces the 5-row ledger and failed suffix case.
