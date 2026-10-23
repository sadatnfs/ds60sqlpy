# cpp-004: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A branch chooses one path using a Boolean condition. A loop repeats a body while its condition holds. An invariant is a fact that remains true before and after each iteration. A boundary is an input where a decision changes, such as zero for a nonnegative reading. Tracing the index, current value and running total makes hidden state visible.

## Detailed reasoning

Trace [4,-2,0,6] as four transitions. Starting total 0 becomes 4 after the first item, stays 4 for the rejected -2, stays 4 for the accepted zero and becomes 10 for 6. The zero step explains why comparing totals alone cannot detect >0 versus >=0: acceptance counts expose the difference. An index loop should state a half-open interval such as [0,size), so an empty input naturally executes zero iterations.

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

Trace [4,-2,0,6] with a row for each input.

**Expected:** Totals [4,4,4,10], four visits.

**Reasoning:** Only the negative value is excluded.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Change the threshold

Count retained values for >=0 and >0 on [4,-2,0,6].

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

Keep readings in [0,5] from [-1,0,4,5,6].

**Expected:** Values [0,4,5], total 9.

**Reasoning:** Use conjunction with both inclusive boundaries.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
