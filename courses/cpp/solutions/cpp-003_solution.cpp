#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>

int main() {
  const int whole = 7 / 2;
  const double fractional = 7.0 / 2.0;
  const double promoted = static_cast<double>(7) / 2;
  if (whole != 3 || fractional != 3.5 || promoted != 3.5)
    return 1;
  const double truncatedThenConverted = static_cast<double>(7 / 2);
  if (truncatedThenConverted != 3.0)
    return 2;
  const long long external = -1;
  if (external >= 0)
    return 3;
  const std::int64_t wide = 1000000LL * 10000LL;
  if (wide != 10000000000LL)
    return 4;
  const int cents = 125 + 75;
  if (cents != 200)
    return 5;
  const int positive = 3;
  const std::size_t count = static_cast<std::size_t>(positive);
  if (count != 3U)
    return 6;
  std::cout << "whole=3 fractional=3.5 promoted=3.5 late=3\n";
  std::cout << "negative rejected; wide=" << wide << "; cents=" << cents
            << '\n';
  return 0;
}

// Exercise 1: Predict integer division. Inputs: 7/2 and7.0/2.0. Expected: 3 and3.5. Verify: compare both numeric results and explain operand types.
// Exercise 2: Place the conversion correctly. Inputs: static_cast<double>(7)/2 versus static_cast<double>(7/2). Expected: 3.5 versus3.0. Verify: assert both results and identify the inner expression evaluated first.
// Exercise 3: Guard a signed count. Inputs: long long external=-1. Expected: rejected; no unsigned index or allocation follows. Verify: inspect the guard-before-cast order and a nonnegative control case3.
// Exercise 4: Widen operands before multiplication. Inputs: 1000000LL*10000LL. Expected: 10000000000 in a64-bit-capable type. Verify: assert the exact number; explain why casting an overflowing int product afterward is too late.
// Exercise 5: Use exact cents for this fixture. Inputs: 125 cents and75 cents. Expected: 200 cents. Verify: assert integral result200 and label its unit explicitly.
// Exercise 6: Transfer a valid small size. Inputs: positive=3, known representable by size_t. Expected: count3; zero would also be valid, while-1 is not. Verify: test3 and0 after validation and explain that arbitrary huge values still need a range check.
