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

struct Cents { long long value; bool operator==(const Cents&)const=default; };
Cents operator+(Cents a,Cents b){return Cents{a.value+b.value};}
int main() {
    Cents a{125},zero{0}; assert((a+zero)==a); assert((Cents{25}+Cents{100})==a);
    assert(a==Cents{125});
    // Reference extension checks for the exercise changes.
    Cents b{125},c{125};assert(a==b&&b==a&&b==c&&a==c);
    std::cout << "cpp-021 examples passed\n";
    return 0;
}


// Exercise 1: Name the units. Compare Cents{125} with item count 125. Expected: Equal representation, different domain meaning.
// Exercise 2: Test identity. Add zero to Cents{125}. Expected: Cents{125}.
// Exercise 3: Construct a separate type. Add struct ItemCount and avoid mixed addition. Expected: Cents+ItemCount has no valid overload.
// Exercise 4: Repair implicit conversion. Review a non-explicit raw integer constructor. Expected: Use explicit construction at the domain boundary.
// Exercise 5: Check equality laws. Compare a=125,b=125,c=125. Expected: Reflexive, symmetric and transitive equality for these values.
// Exercise 6: Transfer safety. Specify checked addition when values approach LLONG_MAX. Expected: Reject overflow before calculating a+b.
