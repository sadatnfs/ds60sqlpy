# cpp-019: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A range combines an iterable start and end. A view can lazily filter or transform a range without owning a new collection. Laziness means the work happens during traversal, so later owner changes can affect what is seen. A projection selects a member for an algorithm without changing the record.

## Detailed reasoning

A lazy filter does not produce a new vector when it is declared. Iteration asks the source for successive values, applies the predicate and then transforms accepted values. The view therefore shares the source lifetime and may observe source changes. Materializing [0,6] makes a stable owned result. Sorting Score by a projection reorders whole records rather than sorting a detached points column, which preserves each ID-to-points relationship.

## Worked example 1

```cpp
auto view=xs|std::views::filter([](int x){return x>=0;});
```

Expected: For [-1,0,3], traversal yields 0 and 3.

## Worked example 2

```cpp
std::ranges::sort(scores,{},&Score::points);
```

Expected: Records order by points while carrying their original IDs.

## Exercise 1: Predict lazy output

Filter >=0 then double [-1,0,3].

**Expected:** [0,6].

**Reasoning:** The predicate runs before transformation.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Change composition

Double first, then filter >0.

**Expected:** [6]; zero is excluded by the new predicate.

**Reasoning:** Changing order or boundary changes the contract.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Materialize ownership

Collect the view into vector<int>.

**Expected:** Stored [0,6] remains independent of later source changes.

**Reasoning:** Materialization gives the result ownership.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair dangling view

Review a view returned over a local vector.

**Expected:** Reject; keep the owner outside or return a vector.

**Reasoning:** A lazy pipeline still borrows the original storage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Sort records

Sort scores (id1,9),(id2,4) by points.

**Expected:** ID order [2,1].

**Reasoning:** Projection selects the comparison key, not the output type.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer stable ties

Add (id3,4) and define deterministic ordering by points then ID.

**Expected:** ID order [2,3,1].

**Reasoning:** A tie-breaker makes equal-key order explicit.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
