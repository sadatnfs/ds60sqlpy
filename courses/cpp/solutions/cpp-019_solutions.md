# cpp-019: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A range combines an iterable start and end. A view can lazily filter or transform a range without owning a new collection. Laziness means the work happens during traversal, so later owner changes can affect what is seen. A projection selects a member for an algorithm without changing the record.

## Detailed reasoning

A lazy filter does not produce a new vector when it is declared. Iteration asks the source for successive values, applies the predicate and then transforms accepted values. The view therefore shares the source lifetime and may observe source changes. Materializing [0, 6] makes a stable owned result. Sorting Score by a projection reorders whole records rather than sorting a detached points column, which preserves each ID-to-points relationship.

<!-- depth:start -->
## Lazy ranges, predicates and projections

A range provides a sequence to traverse. A view is commonly a lightweight, lazy description of a transformation over a range. Building a filter view does not necessarily evaluate the predicate for every element immediately. Iteration performs the work needed to produce values. This distinction matters when the underlying data changes or a predicate has side effects.

The first program filters [-1, 0, 3] with x>=0 and materializes the observed result into a vector. Zero is retained because the boundary is inclusive. The view itself does not erase -1 from the original vector. Materialization creates an owning result with a stable sequence independent of later changes to the input. Without that step, the view remains coupled to its source and its lifetime/invalidation rules.

The projection in ranges::sort(scores, {}, &Score::points) selects which member participates in comparison. The empty braces choose the default comparator; the member pointer supplies a projection from Score to points. Sorting moves whole Score values, so IDs remain attached to their corresponding points. Sorting a separate points vector without preserving identity would answer a different question.

A predicate should be understandable as a rule over an element. Side effects such as incrementing an external counter can make the result depend on how often and when the range implementation evaluates it. Do not use an assumed predicate-call count as a business result unless the algorithm explicitly guarantees it. Keep counting as a separate deliberate operation when that count is part of the contract.

Views also require care around temporary owners. A pipeline that safely owns or references its source under one type combination is not proof that every returned view survives. When a function returns a filtered result for later use, an owning vector may be the simplest correct interface. The later generic-pipeline lesson develops this boundary for single-pass input ranges.

## Debugging the contract

If the original vector changed after filtering, inspect whether the code actually used an erasing algorithm. If a view later reads garbage, trace its owner lifetime and invalidation. If IDs no longer match scores, check whether fields were sorted separately. If a lambda counter produces a surprising total, remove side effects and reason from the algorithm's traversal contract rather than guessing how many times the predicate runs.
<!-- depth:end -->

## Worked example 1

```cpp
auto view=xs|std::views::filter([](int x){return x>=0;});
```

Expected: For [-1, 0, 3], traversal yields 0 and 3.

## Worked example 2

```cpp
std::ranges::sort(scores,{},&Score::points);
```

Expected: Records order by points while carrying their original IDs.

## Exercise 1: Predict lazy output

Filter >=0 then double [-1, 0, 3].

**Expected:** [0, 6].

**Reasoning:** The predicate runs before transformation.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Change composition

Double first, then filter >0.

**Expected:** [6]; zero is excluded by the new predicate.

**Reasoning:** Changing order or boundary changes the contract.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Materialize ownership

Collect the view into vector<int>.

**Expected:** Stored [0, 6] remains independent of later source changes.

**Reasoning:** Materialization gives the result ownership.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair dangling view

Review a view returned over a local vector.

**Expected:** Reject; keep the owner outside or return a vector.

**Reasoning:** A lazy pipeline still borrows the original storage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Sort records

Sort scores (id1, 9), (id2, 4) by points.

**Expected:** ID order [2, 1].

**Reasoning:** Projection selects the comparison key, not the output type.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer stable ties

Add (id3, 4) and define deterministic ordering by points then ID.

**Expected:** ID order [2, 3, 1].

**Reasoning:** A tie-breaker makes equal-key order explicit.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
