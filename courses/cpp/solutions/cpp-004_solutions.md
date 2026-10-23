# cpp-004: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A branch chooses one path using a Boolean condition. A loop repeats a body while its condition holds. An invariant is a fact that remains true before and after each iteration. A boundary is an input where a decision changes, such as zero for a nonnegative reading. Tracing the index, current value and running total makes hidden state visible.

## Detailed reasoning

Trace [4, -2, 0, 6] as four transitions. Starting total 0 becomes 4 after the first item, stays 4 for the rejected -2, stays 4 for the accepted zero and becomes 10 for 6. The zero step explains why comparing totals alone cannot detect >0 versus >=0: acceptance counts expose the difference. An index loop should state a half-open interval such as [0, size), so an empty input naturally executes zero iterations.

<!-- depth:start -->
## State, boundaries and loop progress

A loop has three questions: what state is carried, which element is visited next, and why does the process terminate? In nonnegative_sum, the carried state is total. Immediately before each iteration, total equals the sum of the nonnegative values in the already visited prefix. Initially that prefix is empty, so zero is the correct state. After processing4 the prefix sum is 4; after -2 it stays4; after 0 it stays4; after 6 it becomes10. This is an invariant, not merely a description of one lucky output.

The range-for declaration `int x : xs` copies the current integer into x. Changing x would not change the vector element. The body executes once per element and never for an empty vector. No special empty-case index is needed because the traversal contract already handles zero elements. An index loop requires more care: for a vector of size n, valid indices are0 through n-1, while n is the past-the-end position. Using <=size instead of <size creates an invalid access on the final iteration.

A boundary bug can be hidden by an aggregate. Replacing >=0 with >0 changes whether zero is retained, but adding zero does not change the total. Therefore a total-only test cannot distinguish those predicates. Track both accepted count and sum when the policy cares about membership. The empty, all-negative and mixed fixtures exercise different paths; none substitutes for the exact zero boundary.

Loop initialization belongs outside the repeated body when it represents accumulated history. If total is reset to zero at each iteration, the program forgets every prior contribution and may return only the last accepted value. A trace table exposes that defect immediately. The same principle applies to counters, maximum-so-far values and parser state: choose an initial identity and explain the transition before writing the loop.

Termination also has an input-budget dimension. The vector example is finite and bounded, while a stream loop can continue as long as data arrives. A production reader therefore needs a declared row or byte budget as well as a correct loop condition. These small values fit in int; a later lesson addresses overflow. Correct traversal alone does not make unbounded arithmetic safe.

## Debugging the contract

When the sum is wrong, inspect the first iteration where the invariant fails. Keep columns for index, current value, predicate result and total before/after. If the total is correct but the accepted count is wrong, test zero specifically. If a loop crashes only on empty input, look for an unconditional first-element access or unsigned size-1 calculation. Do not repair a boundary failure by discarding the failing row without defining that input policy.
<!-- depth:end -->

## Worked example 1

```cpp
assert(nonnegative_sum({4,-2,0,6})==10);
```

Expected: The running total is 4, 4, 4, 10.

## Worked example 2

```cpp
assert(nonnegative_sum({})==0);
```

Expected: The body runs zero times; the initial total is the result.

## Exercise 1: Trace state

Trace [4, -2, 0, 6] with a row for each input.

**Expected:** Totals [4, 4, 4, 10], four visits.

**Reasoning:** Only the negative value is excluded.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Change the threshold

Count retained values for >=0 and >0 on [4, -2, 0, 6].

**Expected:** Counts 3 and 2; both sums 10.

**Reasoning:** A sum can hide a zero-boundary error.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Construct a bounded loop

Sum integers 1 through 4 with an index loop.

**Expected:** 10 from exactly four iterations.

**Reasoning:** Use i<=4 or an equivalent half-open range.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair a reset

Move total=0 into the loop, predict, then repair the scratch copy.

**Expected:** Broken final total 6; repaired total 10.

**Reasoning:** Initialization inside the loop forgets earlier state.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Test the empty boundary

Run empty and all-negative vectors.

**Expected:** Both totals 0; no element access.

**Reasoning:** The invariant starts valid before any iteration.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer the predicate

Keep readings in [0, 5] from [-1, 0, 4, 5, 6].

**Expected:** Values [0, 4, 5], total 9.

**Reasoning:** Use conjunction with both inclusive boundaries.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
