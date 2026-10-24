#include <cstddef>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <utility>
#include <vector>

namespace ds60 {
long long positive_sum(const std::vector<int> &readings) {
  long long total = 0;
  for (const int value : readings) {
    if (value > 0)
      total += value;
  }
  return total;
}

bool replace_at(std::vector<int> &readings, std::size_t index,
                int replacement) {
  if (index >= readings.size())
    return false;
  readings.at(index) = replacement;
  return true;
}

std::optional<int> checked_read(const std::vector<int> &readings,
                                long long index) {
  if (!std::in_range<std::size_t>(index))
    return std::nullopt;
  const auto position = static_cast<std::size_t>(index);
  if (position >= readings.size())
    return std::nullopt;
  return readings.at(position);
}

std::vector<int> nonnegative_copy(const std::vector<int> &readings) {
  std::vector<int> result;
  for (const int value : readings) {
    if (value >= 0)
      result.push_back(value);
  }
  return result;
}
} // namespace ds60
int main() {
  std::vector<int> original{4, 7, 9};
  const auto copy = original;
  original.at(0) = 5;
  if (copy.at(0) != 4 || original.at(0) != 5)
    return 1;
  std::cout << "copy=" << copy.at(0) << " original=" << original.at(0) << '\n';
  try {
    (void)original.at(original.size());
    return 2;
  } catch (const std::out_of_range &) {
    std::cout << "bounds rejected\n";
  }
  return 0;
}
// Exercise 1: Predict copy3 versus alias4 for values{3,8}, then retain an ownership trace.
// Exercise 2: positive_sum reads at most10000 integers in[-1000000,1000000]; mixed result20 and large result10000000000.
// Exercise 3: replace_at changes valid index1; index==size and empty input return false without mutation.
// Exercise 4: Repair the borrowed-element proposal using an owned snapshot or a checked later lookup; never run a dangling read.
// Exercise 5: checked_read rejects negative, one-past and unrepresentable signed indices before casting.
// Exercise 6: nonnegative_copy({3,-1,0,5}) returns independent{3,0,5}; source remains unchanged.
