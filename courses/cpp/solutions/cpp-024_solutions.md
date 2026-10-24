# cpp-024: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A property describes a relation that should hold across many inputs. A golden fixture supplies independently chosen expected values. A corpus retains useful edge and failure cases. Bounded fuzzing explores a finite input budget and saves the exact failing case so a defect can be reproduced.

## Detailed reasoning

An implementation that returns its input unchanged satisfies double reversal, so that law alone cannot identify reversal. The literal [1, 2, 3] to [3, 2, 1] example supplies an independent semantic anchor. The 25 two-element cases then explore combinations systematically. When a test fails, retain the smallest relevant vector and observed result, not only a random seed. A limited corpus plus explicit budgets is reproducible evidence with a visible coverage boundary.

<!-- depth:start -->
## Tests that distinguish plausible wrong programs

A useful test is chosen to reject a plausible defect. One expected example can show a behavior, but it may also be satisfied by a shortcut that returns a constant. Boundary cases, negative cases and independent properties make the contract harder to fake accidentally. The reverse example starts with a concrete known result, then checks a relationship over changed inputs.

Reversing twice should recover the original sequence. This is a metamorphic property: it relates outputs of multiple executions without requiring a handwritten expected vector for every possible input. However, the identity function also satisfies reverse(reverse(x))==x. Therefore the property must be paired with an ordinary example whose expected order differs from its input. Properties complement examples; they do not automatically prove the intended algorithm.

Empty and single-element sequences are important because they expose invalid index calculations. For an unsigned size, computing size-1 on an empty vector wraps before a loop even begins. A standard algorithm can avoid that hand-written boundary hazard, but the input contract still needs tests. Repeated values check multiplicity preservation rather than only order.

A deterministic corpus is easier to reproduce than an unexplained random failure. If randomized generation is used, record the seed and the minimized failing input, but do not assume the seed alone remains sufficient after generator changes. A small exact counterexample usually teaches more than thousands of passing cases. Test reporting should retain the first meaningful mismatch rather than hide it in a large log.

Mutation testing asks whether the test suite rejects a deliberately wrong implementation, such as returning the input unchanged or dropping one repeated value. The exercise can perform that change in a scratch copy and compare which test catches it. Do not weaken the expectation to accept the mutated behavior. The purpose is to assess whether the tests cover the contract, not whether every edited program can be made green.

## Debugging the contract

If a property passes for a wrong implementation, construct a concrete case that distinguishes the intended transformation from the shortcut. If only empty input crashes, inspect size arithmetic before indexing. If a randomized failure cannot be reproduced, preserve the exact input in addition to the seed. If all tests compare a function with itself through the same helper, add an independent oracle or manually derived expected value.
<!-- depth:end -->

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

Reverse [1, 2, 3] against a literal expected vector.

**Expected:** [3, 2, 1].

**Reasoning:** The expected result is independent of the implementation.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Enumerate a property

Test all pairs from integers -2 through 2.

**Expected:** 25 cases satisfy double reversal.

**Reasoning:** The finite domain gives a known work budget.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Add a boundary corpus

Include empty, singleton and duplicate vectors.

**Expected:** [], [7], [2, 2] preserved after double reversal.

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
