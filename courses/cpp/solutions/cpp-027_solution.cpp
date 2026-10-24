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

namespace vendored { constexpr int api_version=1; constexpr int add(int a,int b){return a+b;} }
int main() {
    static_assert(vendored::api_version==1);assert(vendored::add(2,3)==5);
    // Reference extension checks for the exercise changes.
    assert(vendored::add(0,0)==0);assert(vendored::add(-2,2)==0);
    std::cout << "cpp-027 examples passed\n";
    return 0;
}


// Exercise 1: Inventory inputs. List compiler, C++ level, dependency source and build generator. Expected: Four concrete identities, including dependency content hash.
// Exercise 2: Build offline. Build the supplied local target in a fresh owned directory without network. Expected: Configure/build/test complete without downloads.
// Exercise 3: Expose target requirements. Create a CMake interface target with cxx_std_20. Expected: Consumer inherits the required language feature.
// Exercise 4: Repair hidden fetch. Review a configure script that downloads latest.zip. Expected: Replace with checked local source and pinned reviewed identity.
// Exercise 5: Check licensing. Package the dependency license with the source inventory. Expected: License path present in the delivery tree.
// Exercise 6: Transfer another platform. Record an untested architecture as unqualified. Expected: Separate built platform from planned platforms.
