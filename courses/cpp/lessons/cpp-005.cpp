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

int clamp_reading(int x,int low,int high) { if(low>high) throw std::invalid_argument("reversed bounds"); return std::max(low,std::min(x,high)); }
int main() {
    assert(clamp_reading(12,0,10)==10);
    assert(clamp_reading(-3,0,10)==0);
    assert(clamp_reading(5,0,10)==5);
    bool rejected=false; try { (void)clamp_reading(5,10,0); } catch(const std::invalid_argument&) { rejected=true; } assert(rejected);
    std::cout << "cpp-005 examples passed\n";
    return 0;
}


// Exercise 1: Predict the contract. Evaluate -3,5,12 for bounds [0,10]. Expected: Results [0,5,10].
// Exercise 2: Check parameter isolation. Call with variable x=12 and inspect x afterward. Expected: Result 10; caller x still 12.
// Exercise 3: Build a predicate. Write inside(x,low,high) with inclusive bounds. Expected: inside(0,0,10) true; inside(11,0,10) false.
// Exercise 4: Repair an invalid contract. Remove the reversed-bounds check and explain the lost guarantee. Expected: clamp(5,10,0) must be rejected after repair.
// Exercise 5: Check a one-point interval. Evaluate x=2,3,4 with bounds [3,3]. Expected: All return 3.
// Exercise 6: Transfer to money. Clamp a cents amount of 1250 to [0,1000]. Expected: 1000 integer cents, without floating conversion.
