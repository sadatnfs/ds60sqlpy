# cpp-009 explanatory solutions

Design preview, checked 2026-10-22. These answers correspond to the six tasks in the [learner pilot](cpp-pilot.md). They are separate from the default learner view. A reader should attempt the task or explicitly request a reveal first. This document supplies reasoning and example implementations; it does not activate a compiler adapter.

## 1. Copy versus alias prediction

The answer is `snapshot.at(0)==3`, `alias.at(0)==4` and `values.size()==2`.

`auto snapshot = values` creates a vector value with independent elements. `const auto& alias = values` binds another access path to the existing vector. Assignment through `values` changes that existing vector, so the alias sees4. `const` forbids mutation through `alias`; it does not prohibit all other valid access paths from changing the same object.

**Expected:** an explicit check for each value and size exits0. A drawing has two owning vector boxes and an arrow from `alias` to the original box. The objects' addresses need not have any particular relationship.

**Verify:** changing the original again changes the alias observation but leaves the copied snapshot unchanged. Replacing the copy declaration with a reference changes this result, which is a useful controlled counterexample.

## 2. Sum positive readings with a wide accumulator

```cpp
long long positive_sum(const std::vector<int>& readings) {
    long long total = 0;
    for (const int value : readings) {
        if (value > 0) total += value;
    }
    return total;
}
```

The const reference avoids an unnecessary input copy and prevents this function from mutating through its parameter. `total` is `long long`, not the element's `int` type. Under the stated bounds, the largest sum is 10000 multiplied by 1000000, or 10000000000, which is representable by the standard's minimum 64-bit `long long` range.

**Expected:** `{4,-2,7,0,9}` produces 20; empty/all-negative inputs produce 0; the large fixture produces 10000000000. The input remains equal to its saved copy.

**Verify:** all four sum checks in the independent program pass. A solution using an `int` total can pass the small fixture and fail the large one; signed overflow is undefined behavior, not an acceptable alternative result. This contract does not promise safe accumulation for arbitrarily large vectors or values outside its declared bounds.

## 3. Replace only a valid position

```cpp
bool replace_at(std::vector<int>& readings, std::size_t index, int replacement) {
    if (index >= readings.size()) return false;
    readings.at(index) = replacement;
    return true;
}
```

The mutable reference is intentional: this task changes the caller's vector. The guard includes equality because `size()` is one past the final element. Nothing is inserted and no vector capacity change is needed.

**Expected:** index 1 changes `{4,7,9}` to `{4,8,9}` and returns true. Index3 and empty/index 0 return false without mutation.

**Verify:** compare both the Boolean and the complete vector for all three fixtures. Checking only a returned flag would miss a function that mutates before rejecting. Using unchecked indexing before the guard would violate the contract even if one run appeared correct.

## 4. Repair the element lifetime deliberately

For an old snapshot, own the integer value:

```cpp
std::vector<int> values{4, 7, 9};
const int snapshot = values.at(0);
values.push_back(11);
values.at(0) = 6;
if (snapshot != 4 || values.size() != 4) return 1;
```

For the current value after append-only growth, keep a position and fetch after the change:

```cpp
std::vector<int> values{4, 7, 9};
const std::size_t first_index = 0;
values.push_back(11);
values.at(0) = 6;
const int current = values.at(first_index);
if (current != 6 || values.size() != 4) return 1;
```

**Expected:** the old snapshot is 4, the newly fetched current value is 6, and both variants have size 4. The original borrowed-reference proposal has no reliable output contract after a possible reallocation, so it is not executed as a test.

**Verify:** run only these safe variants, then explain the diagram: vector growth may end the old element-storage lifetime, whereas the owned integer remains alive and an index is only a position used for a later checked lookup. If elements were erased or reordered, the same position might refer to a different logical record. An index is not a universal identity mechanism. Calling `reserve` can help within a carefully stated capacity bound, but it is not a substitute for reasoning about all invalidating operations.

## 5. Validate representation before conversion

```cpp
std::optional<int> checked_read(const std::vector<int>& readings, long long index) {
    if (!std::in_range<std::size_t>(index)) return std::nullopt;
    const auto position = static_cast<std::size_t>(index);
    if (position >= readings.size()) return std::nullopt;
    return readings.at(position);
}
```

Include `<utility>` for `std::in_range`. This tests negative or too-large values before converting them. The second guard asks a different question: even if the type can represent the index, does this particular vector contain that position? Returning an optional value creates an independent integer result rather than exporting a borrowed element reference.

**Expected:** index 1 yields7; -1, size 3/index 3 and empty/index 0 yield no value. The input remains unchanged.

**Verify:** all four published read checks pass, and the learner states both guard purposes. A cast-first implementation is fragile on a narrower index type: a large external integer can wrap into a small index. A supported 64-bit build alone does not prove that such a cast-first implementation is portable.

## 6. Return an independently owned filtered batch

```cpp
std::vector<int> nonnegative_copy(const std::vector<int>& readings) {
    std::vector<int> result;
    for (const int value : readings) {
        if (value >= 0) result.push_back(value);
    }
    return result;
}
```

The source is borrowed read-only during the call. The result owns new elements and preserves encounter order. Returning this vector value transfers the result to the caller through normal value semantics; no manual pointer ownership is introduced.

**Expected:** `{3,-1,0,5}` becomes `{3,0,5}`. Empty/all-negative inputs produce an empty vector. Changing the result's first value to99 leaves the source's first value3.

**Verify:** all three filtering checks pass, including input immutability and independence after result mutation. Reusing the input as output would fail those checks. This lesson does not claim that reserving capacity or changing syntax necessarily improves performance; that requires a later measured comparison.

## Complete exercise implementation

Save this as `exercises.cpp` only after comparing your attempt. It matches the declarations and check program in the learner guide.

```cpp
#include "exercises.hpp"
#include <utility>

namespace ds60 {
long long positive_sum(const std::vector<int>& readings) {
    long long total = 0;
    for (const int value : readings) {
        if (value > 0) total += value;
    }
    return total;
}

bool replace_at(std::vector<int>& readings, std::size_t index, int replacement) {
    if (index >= readings.size()) return false;
    readings.at(index) = replacement;
    return true;
}

std::optional<int> checked_read(const std::vector<int>& readings, long long index) {
    if (!std::in_range<std::size_t>(index)) return std::nullopt;
    const auto position = static_cast<std::size_t>(index);
    if (position >= readings.size()) return std::nullopt;
    return readings.at(position);
}

std::vector<int> nonnegative_copy(const std::vector<int>& readings) {
    std::vector<int> result;
    for (const int value : readings) {
        if (value >= 0) result.push_back(value);
    }
    return result;
}
}
```

With the exercise option enabled, the intended acceptance is two passing CTest tests, the worked example's two exact output lines and `14 checks passed` from the exercise program. Repeat the checks in a separate Release build. A direct compiler check of these snippets is narrower evidence than a CMake/CTest run or a proven browser compiler adapter. Native platform and sanitizer claims require their own actual transcripts.

## Review rubric and retrieval

A strong explanation names the owner, the lifetime, the access contract and the observable boundary. Use the learner rubric: at least 8/10, all fourteen function checks, safe Exercise4 variants and an independent transfer explanation. A learner who copied these implementations but cannot explain why `index==size()` fails, why `const` does not freeze aliases or why a dangling read is not a valid experiment needs another prediction/transfer attempt.

Next, replace the integer fixtures with a small record containing an ID and reading. Explain which part of the design changes and which ownership/boundary arguments remain. No new solution is automatically revealed by finishing this page.
