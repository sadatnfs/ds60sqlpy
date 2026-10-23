# cpp-007: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A vector owns a contiguous sequence and knows its current size. An iterator identifies a position for a standard algorithm. Algorithms separate traversal from intent: sorting orders values, counting measures a predicate, and accumulation combines values. Sorting a copy preserves the original evidence.

## Detailed reasoning

A vector is a bag of ordered elements, not a set. The two threes in [3,1,3,0] occupy separate positions after sorting. Erasing duplicates is a new semantic decision. The common sort/unique/erase sequence has two phases after sorting: unique rearranges the retained prefix and returns a new logical end, while erase changes vector size. Inspect both the values and size so a stale tail cannot masquerade as a unique result.

## Worked example 1

```cpp
std::vector<int> xs{3,1,3,0}; std::sort(xs.begin(),xs.end());
```

Expected: The sorted bag is [0,1,3,3], preserving both threes.

## Worked example 2

```cpp
std::vector<int> xs; auto sum=std::accumulate(xs.begin(),xs.end(),0LL);
```

Expected: The empty sum is 0, and begin equals end.

## Exercise 1: Predict sorting

Sort [3,1,3,0] on paper.

**Expected:** [0,1,3,3], size 4.

**Reasoning:** Ordering does not remove multiplicity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Preserve evidence

Sort a copy and compare the original.

**Expected:** Original remains [3,1,3,0].

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

Sort [3,1,3,0], then erase the unique tail.

**Expected:** [0,1,3], size 3.

**Reasoning:** unique moves survivors but erase actually changes vector size.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
