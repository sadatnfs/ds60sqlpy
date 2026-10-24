# cpp-018: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A view borrows a region owned elsewhere. span observes contiguous elements and string_view observes characters. An iterator can be invalidated when its container reallocates or erases elements. None of these lightweight handles extends the owner lifetime, and const views do not prevent the owner from changing through another path.

## Detailed reasoning

A span consists conceptually of an address and a count. Copying a span copies that description, not the elements. Vector growth can replace the allocation while leaving the copied descriptions unchanged. This is why even a const span may dangle after mutation through the owner. For subranges, first establish offset<=size, then count<=size-offset; subtracting only after the first check avoids unsigned underflow in the validation itself.

<!-- depth:start -->
## Views describe storage without owning it

A span describes a contiguous sequence using an address and an extent. A string_view describes characters similarly. Neither owns the underlying storage. Copying a view copies that description, not the elements, so the owner must remain alive and its storage valid for every use. A view is useful for avoiding unnecessary copies only when that lifetime relationship is clear.

The first program borrows a vector through span<const int> and selects subspan(1, 2). The offset1 skips the first element and count 2 selects4 and 6. The sum is 10. The operation does not allocate a new vector. The caller must satisfy the subspan bounds; a view type does not make every offset/count automatically safe. Validate externally supplied ranges before constructing or slicing views.

The second program creates a two-character view over alpha. Changing the first character of the owning string in place makes the view observe Al. This illustrates aliasing: the view is not a frozen snapshot. A string reallocation or destruction would instead invalidate the view. The safe example changes an existing character without altering storage capacity and checks the result while the owner remains in scope.

Const in span<const int> blocks writing elements through that view. It does not prevent another mutable alias from changing the same vector. A function that needs a stable snapshot across later mutation should own a copy or establish a stronger synchronization/lifetime contract. Read-only access and immutable data are different promises.

Returning a view requires identifying an owner that survives the function. Returning a span into a local vector is dangling immediately after return. Returning an owning vector is often the clearer result when the function creates new data. A view into a caller-owned object can be appropriate, but the caller must know which later edits or destruction invalidate it. Document those operations alongside the return type.

## Debugging the contract

A view that worked once can still be dangling. Inspect owner scope and reallocating operations rather than trusting printed bytes. If a returned view points into a local temporary, change the ownership design. If a span slice is out of range, fix the offset/count contract before access. If a supposedly constant result changes, check whether the program borrowed a mutable owner instead of taking a snapshot.
<!-- depth:end -->

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

Sum the final two values of [2, 4, 6].

**Expected:** 10 with original vector unchanged.

**Reasoning:** The borrowed slice starts at offset 1.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Write a bounds guard

Validate offset=2, count=2 for size=3 before subspan.

**Expected:** Reject because only one value remains.

**Reasoning:** Avoid overflow by checking count<=size-offset after offset<=size.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair invalidation

Review span created before vector growth that reallocates.

**Expected:** Recreate span after growth; never dereference stale span.

**Reasoning:** Reallocation replaces the underlying buffer.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test empty view

Pass an empty span to `sum_view`.

**Expected:** 0 without dereference.

**Reasoning:** An empty range has a valid identity total.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer lifetime reasoning

Review string_view returned from a local string.

**Expected:** Reject; return string ownership or borrow caller-owned text.

**Reasoning:** A view cannot retain a destroyed local buffer.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
