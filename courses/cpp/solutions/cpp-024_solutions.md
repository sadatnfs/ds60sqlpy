# cpp-024: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A property describes a relation that should hold across many inputs. A golden fixture supplies independently chosen expected values. A corpus retains useful edge and failure cases. Bounded fuzzing explores a finite input budget and saves the exact failing case so a defect can be reproduced.

## Worked example 1

```cpp
assert((reversed({1,2,3})==std::vector<int>{3,2,1}));
```

Expected: The independent golden example fixes the intended meaning of reversal.

## Worked example 2

```cpp
assert(reversed(reversed(std::vector<int>{-1,2}))==std::vector<int>({-1,2}));
```

Expected: Applying reversal twice restores the original sequence.

## Exercise 1: Write a golden case

Reverse [1,2,3] against a literal expected vector.

**Expected:** [3,2,1].

**Reasoning:** The expected result is independent of the implementation.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Enumerate a property

Test all pairs from integers -2 through 2.

**Expected:** 25 cases satisfy double reversal.

**Reasoning:** The finite domain gives a known work budget.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Add a boundary corpus

Include empty, singleton and duplicate vectors.

**Expected:** [], [7], [2,2] preserved after double reversal.

**Reasoning:** Edges exercise different shapes.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Expose a weak property

Replace reversal with identity in a scratch copy.

**Expected:** Double-reverse property passes but golden reversal fails.

**Reasoning:** A property can be necessary without being sufficient.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Save a reproduction

Break reversal to drop the first item.

**Expected:** Small failing vector and exact observed output retained.

**Reasoning:** A minimized failing case is easier to diagnose than a seed alone.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer to a parser

Design encode/decode properties and independent malformed inputs.

**Expected:** Round-trip valid records; reject suffix junk and wrong versions.

**Reasoning:** Round-trip tests alone can let matching bugs agree.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
