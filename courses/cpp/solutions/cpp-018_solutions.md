# cpp-018: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A view borrows a region owned elsewhere. span observes contiguous elements and string_view observes characters. An iterator can be invalidated when its container reallocates or erases elements. None of these lightweight handles extends the owner lifetime, and const views do not prevent the owner from changing through another path.

## Worked example 1

```cpp
std::vector<int> xs{2,4,6}; assert(sum_view(std::span<const int>(xs).subspan(1,2))==10);
```

Expected: The view of positions 1 and 2 sums to 10.

## Worked example 2

```cpp
std::string text="alpha"; std::string_view prefix(text.data(),2);
```

Expected: The borrowed prefix is al while text remains alive and stable.

## Exercise 1: Identify ownership

Draw vector storage and its span.

**Expected:** One owner and one non-owning view.

**Reasoning:** A view stores a location and length.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Select a subrange

Sum the final two values of [2,4,6].

**Expected:** 10 with original vector unchanged.

**Reasoning:** The borrowed slice starts at offset 1.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Write a bounds guard

Validate offset=2,count=2 for size=3 before subspan.

**Expected:** Reject because only one value remains.

**Reasoning:** Avoid overflow by checking count<=size-offset after offset<=size.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair invalidation

Review span created before vector growth that reallocates.

**Expected:** Recreate span after growth; never dereference stale span.

**Reasoning:** Reallocation replaces the underlying buffer.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test empty view

Pass an empty span to sum_view.

**Expected:** 0 without dereference.

**Reasoning:** An empty range has a valid identity total.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer lifetime reasoning

Review string_view returned from a local string.

**Expected:** Reject; return string ownership or borrow caller-owned text.

**Reasoning:** A view cannot retain a destroyed local buffer.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
