# cpp-003: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/cpp-003.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

The type of an expression controls its arithmetic before assignment. `7/2` divides integers and discards the fractional part, so assigning that result to double later cannot restore the lost half. Converting an operand before division changes the operation. `static_cast<double>(7)/2` therefore differs from `static_cast<double>(7/2)`.

`int` is a signed integer type with implementation-dependent width; do not assume it always has32 bits. `long long` has at least64 bits. `std::int64_t` names an exact64-bit signed type when provided. `std::size_t` is an unsigned size/index type. A cast requests a conversion; it does not validate the original value. First reject a negative external count, then validate the target range where necessary, then convert. Use small fixtures and explicit bounds before reasoning about larger products.

- **integer division:** division of integral operands with discarded fractional part
- **conversion:** changing the representation/type of a value
- **narrowing:** a conversion that can lose range or precision
- **signed/unsigned:** whether the integer representation supports negative values
- **literal suffix:** LL requests long long arithmetic before multiplication

## Worked example / walkthrough

### Worked example 1: Convert before division

The cast belongs to an operand, so floating arithmetic occurs before the result is printed.

```cpp
#include <iostream>
int main(){ std::cout << 7/2 << " " << static_cast<double>(7)/2 << "\n"; }
```

**Expected:** 3 3.5 followed by newline.

### Worked example 2: Reject a negative count

The source never turns the negative value into an unsigned size. The fixture is a validation example, not a request to allocate memory.

```cpp
#include <cstddef>
#include <iostream>
int main(){ const long long count=-1; if(count<0){std::cout<<"rejected\n"; return 0;} return 1; }
```

**Expected:** rejected followed by newline; exit 0 means the intended rejection branch was observed.

## Exercises and explanatory solutions

### Exercise 1: Predict integer division

**Inputs/evidence:** For cpp-003 Exercise 1, 7/2 and 7.0/2.0.

**Expected result/shape:** For cpp-003 Exercise 1, 3 and 3.5.

**Verify:** For cpp-003 Exercise 1, compare both numeric results and explain operand types.

Integer operands request integer division. One floating operand changes the operation; printing precision alone cannot repair a previously truncated integer.

### Exercise 2: Place the conversion correctly

**Inputs/evidence:** For cpp-003 Exercise 2, static_cast<double>(7)/2 versus static_cast<double>(7/2).

**Expected result/shape:** For cpp-003 Exercise 2, 3.5 versus3.0.

**Verify:** For cpp-003 Exercise 2, assert both results and identify the inner expression evaluated first.

The parentheses make the operation order explicit. The late cast converts the already computed3 to 3.0; it cannot recreate a lost fractional part.

### Exercise 3: Guard a signed count

**Inputs/evidence:** For cpp-003 Exercise 3, long long external=-1.

**Expected result/shape:** For cpp-003 Exercise 3, rejected; no unsigned index or allocation follows.

**Verify:** For cpp-003 Exercise 3, inspect the guard-before-cast order and a nonnegative control case3.

Unsigned conversion can make negative values very large. A precondition is about input meaning, not merely whether the compiler accepts a cast.

### Exercise 4: Widen operands before multiplication

**Inputs/evidence:** For cpp-003 Exercise 4, 1000000LL*10000LL.

**Expected result/shape:** For cpp-003 Exercise 4, 10000000000 in a64-bit-capable type.

**Verify:** For cpp-003 Exercise 4, assert the exact number; explain why casting an overflowing int product afterward is too late.

The literal suffixes make the multiplication wide. A wide destination alone does not determine how a narrower operand expression was evaluated.

### Exercise 5: Use exact cents for this fixture

**Inputs/evidence:** For cpp-003 Exercise 5, 125 cents and 75 cents.

**Expected result/shape:** For cpp-003 Exercise 5, 200 cents.

**Verify:** For cpp-003 Exercise 5, assert integral result200 and label its unit explicitly.

An integer has an exact representation for these cents values. A later lesson can introduce decimal rules; this fixture does not need binary fractional money.

### Exercise 6: Transfer a valid small size

**Inputs/evidence:** For cpp-003 Exercise 6, positive=3, known representable by size_t.

**Expected result/shape:** For cpp-003 Exercise 6, count 3; zero would also be valid, while-1 is not.

**Verify:** For cpp-003 Exercise 6, test 3 and 0 after validation and explain that arbitrary huge values still need a range check.

This bounded control demonstrates an intentional conversion. It does not justify casting arbitrary external long long values on every platform without representability validation.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.
