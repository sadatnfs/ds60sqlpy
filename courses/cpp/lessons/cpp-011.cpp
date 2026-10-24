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

std::vector<std::string> read_lines(std::istream &input) {
  std::vector<std::string> out;
  std::string line;
  while (std::getline(input, line))
    out.push_back(line);
  if (input.bad())
    throw std::runtime_error("read failed");
  return out;
}
int main() {
  std::istringstream input("10\n20\n");
  assert((read_lines(input) == std::vector<std::string>{"10", "20"}));
  std::istringstream empty("");
  assert(read_lines(empty).empty());
  std::istringstream no_newline("30");
  assert(read_lines(no_newline).size() == 1);
  std::cout << "cpp-011 examples passed\n";
  return 0;
}

// Exercise 1: Trace successful reads. Read the literal 10-newline-20-newline fixture. Expected: Two records [10,20].
// Exercise 2: Handle empty input. Run read_lines on an empty string stream. Expected: Zero records, ordinary EOF.
// Exercise 3: Write an owned file. In a new scratch directory write two lines, close, reopen and read. Expected: The reopened bytes represent 10 and 20 exactly once.
// Exercise 4: Repair eof-first looping. Compare while(!eof()) with the supplied successful-read loop. Expected: The repaired loop has two records and no stale extra line.
// Exercise 5: Check open failure. Open missing-file.txt for input in a new empty scratch directory. Expected: is_open false or stream failure; report the path and stop.
// Exercise 6: Transfer the path contract. Run from two working directories with the same relative filename. Expected: Different resolved locations; explicit supplied path selects one file.
