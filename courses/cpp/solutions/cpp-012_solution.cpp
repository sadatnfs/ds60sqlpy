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

int add(int, int);
int add(int a, int b) { return a + b; }
int subtract_example(int a, int b) { return a - b; }
int main() {
  assert(add(2, 3) == 5);
  assert(add(0, 0) == 0);
  // Reference extension checks for the exercise changes.
  assert(subtract_example(5, 3) == 2);
  std::cout << "cpp-012 examples passed\n";
  return 0;
}

// Exercise 1: Separate declaration. Split add declaration, definition and caller using the supplied host-project recipe. Expected: math.hpp, math.cpp and main.cpp build one executable returning 5.
// Exercise 2: Compile one object. Compile main.cpp with -c before linking. Expected: main.o exists even though the function body is in math.cpp.
// Exercise 3: Link the complete set. Link main.o and math.o. Expected: Executable runs, exit 0 and value 5.
// Exercise 4: Diagnose missing object. Omit math.o deliberately. Expected: Nonzero link status naming an unresolved add symbol.
// Exercise 5: Diagnose duplicate definition. Put a non-inline add body in a header included by both files. Expected: A duplicate-definition link failure; restore one source definition.
// Exercise 6: Transfer a library boundary. Add subtract declaration and definition and a caller test 5-3. Expected: Result 2 with one definition and matching signature.
