# cpp-007: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A vector owns a contiguous sequence and knows its current size. An iterator identifies a position for a standard algorithm. Algorithms separate traversal from intent: sorting orders values, counting measures a predicate, and accumulation combines values. Sorting a copy preserves the original evidence.

## Detailed reasoning

A vector is a bag of ordered elements, not a set. The two threes in [3, 1, 3, 0] occupy separate positions after sorting. Erasing duplicates is a new semantic decision. The common sort/unique/erase sequence has two phases after sorting: unique rearranges the retained prefix and returns a new logical end, while erase changes vector size. Inspect both the values and size so a stale tail cannot masquerade as a unique result.

<!-- depth:start -->
## Vector ownership, capacity and iterator validity

A vector has a size and a capacity. Size counts constructed elements that the program may access. Capacity describes how many elements the current storage can accommodate before another allocation is needed. reserve(4) requests capacity for at least four elements but leaves an empty vector at size 0. Writing xs[0] after reserve alone is invalid because no element has been constructed there. push_back creates a new element and increases size; resize changes size and constructs or destroys elements as needed.

Contiguous storage means the elements occupy adjacent positions, which makes indexed access and many algorithms efficient. It also explains reallocation. If growth requires a new buffer, the vector moves or copies elements into that buffer and releases the old storage. Every pointer, reference and iterator into the old element storage is then invalid. Do not demonstrate this by dereferencing a stale pointer: that is undefined behavior, so even an apparently correct printed value is not evidence of safety.

The second program forces a capacity increase with reserve(capacity()+1) after adding one element. It retains an index, not an element pointer, and reacquires access as xs[index] after the operation. This is safe for that example because reallocation preserves the sequence and index 0 still names the same element. It is not a general fix for erase or insert before an index, which can change what a position means. Stable business identity may need an ID lookup rather than a remembered position.

begin and end define a half-open range. begin names the first element when one exists; end names the position after the last and must not be dereferenced. Empty vectors have begin==end, so algorithms can handle them without a special invalid first-element access. Sorting rearranges values within the range. It preserves multiplicity: the two threes remain two elements. Copying original before sorting gives a separate owner, so the original order remains available for comparison.

accumulate uses its initial value both as the starting total and to determine the accumulator type. Starting with 0LL selects long long and the additive identity. Starting with 10LL adds an unwanted ten even though the element traversal is otherwise correct. Starting with int0 can introduce a narrower intermediate accumulator for large values. A wider accumulator reduces some overflow risks but is not an unlimited arithmetic guarantee.

The sort/unique/erase idiom has separate contracts. sort brings equal values together. unique rearranges a retained prefix and returns its logical end; it does not shrink the vector. erase removes the tail and changes size. Code that prints the whole vector after unique but before erase can show unspecified leftover tail values and mistakenly believe deduplication failed. Inspect the retained range and final size, not just one displayed element.

Insertion and erasure have their own invalidation rules even when no reallocation occurs. Erasing shifts later elements left, invalidating positions at or after the erased point. The safe iteration pattern uses the iterator returned by erase rather than incrementing an invalid old iterator. These rules matter because a vector is a sequence with ownership and position semantics, not a set or a permanently stable collection of element addresses.

## Debugging the contract

A capacity of 4 with size 0 is not four accessible integers. Use at(index) for a checked diagnostic while learning, and remember that operator[] requires a valid index. If a bug appears only after growth, inspect every retained pointer/reference/iterator across push_back or reserve. If a deduplicated result still has size 4, check whether erase was omitted. If a total differs by ten, inspect the accumulate identity before blaming sort.
<!-- depth:end -->

## Worked example 1

```cpp
std::vector<int> xs{3,1,3,0}; std::sort(xs.begin(),xs.end());
```

Expected: The sorted bag is [0, 1, 3, 3], preserving both threes.

## Worked example 2

```cpp
std::vector<int> xs; auto sum=std::accumulate(xs.begin(),xs.end(),0LL);
```

Expected: The empty sum is 0, and begin equals end.

## Exercise 1: Predict sorting

Sort [3, 1, 3, 0] on paper.

**Expected:** [0, 1, 3, 3], size 4.

**Reasoning:** Ordering does not remove multiplicity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Preserve evidence

Sort a copy and compare the original.

**Expected:** Original remains [3, 1, 3, 0].

**Reasoning:** Copying creates a separately owned buffer.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Count a boundary

Use count_if to count >=3.

**Expected:** 2 matching elements.

**Reasoning:** Both equal-valued rows count.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair a wrong total

Replace accumulate start 0LL with 10LL, then repair.

**Expected:** Wrong total 17; correct total 7.

**Reasoning:** The initial value participates in the fold.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check an empty vector

Sort, count and sum an empty vector.

**Expected:** Size 0, count 0, sum 0; no dereference.

**Reasoning:** Algorithms accept an empty half-open range.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer to ordered unique values

Sort [3, 1, 3, 0], then erase the unique tail.

**Expected:** [0, 1, 3], size 3.

**Reasoning:** unique moves survivors but erase actually changes vector size.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
