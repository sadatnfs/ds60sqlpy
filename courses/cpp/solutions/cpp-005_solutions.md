# cpp-005: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A function names a computation with parameters as inputs and a return value as its output. A precondition is a promise the caller must satisfy. A postcondition describes the result. Pure functions avoid hidden state, so the same inputs produce the same value and small boundary tests are meaningful.

## Detailed reasoning

A caller has three distinct questions: are the bounds valid, is the value below/inside/above them, and may the call alter its input? The supplied function rejects reversed bounds first. Only then does it compute min(value, high), followed by max(low, ...). The three ordinary cases cover each position relative to the interval, while equal bounds test a degenerate but valid interval. A return value can differ from the argument without mutating the caller because parameters are copies.

<!-- depth:start -->
## Function contracts and call boundaries

A function call creates a local computation with a clear interface. The caller supplies x, low and high; the function returns one integer or rejects an invalid interval. Pass by value gives each parameter its own integer value. If the caller stores x=12, calling clamp_reading(x, 0, 10) can return10 while the caller variable remains12. Returning a value and modifying a caller object are different interface choices.

The contract has an ordering dependency. First establish low<=high. Only then does the phrase clamp into the interval have a meaningful interpretation. The expression max(low, min(x, high)) implements the valid interval behavior, but it is not an interval validator. With reversed bounds, those library calls still produce an integer, which can hide a nonsensical request. Explicit rejection preserves the distinction between a valid answer and invalid input.

Trace the three ordinary paths separately. Below the interval, min(x, high) leaves x and max raises it to low. Inside, both operations leave x unchanged. Above, min lowers x to high and max leaves it there. Equal bounds are valid: every input maps to the single permitted point. That fourth case checks that the validation uses > rather than >=.

The exception type communicates why no result is returned. In the second worked program, the catch block sets a flag, and the program asserts that the flag became true. Merely writing an empty catch block would not prove the exception occurred. Uncaught exceptions terminate the program through a different path from an explicit status return, so the caller must choose where to translate failures into a user-facing diagnostic.

For a larger API, document units and ranges as part of the contract. Integer cents and integer degrees use the same C++ type but represent different quantities. A pure clamp function is easy to test because it depends only on its arguments. A hidden global limit or filesystem read would add state that each test and caller must understand. Prefer that extra dependency to be explicit when it is actually needed.

## Debugging the contract

A function-name typo or incompatible argument type is usually a compile problem. A declared but undefined function can compile at the call site and fail during linking. A reversed interval here is a runtime contract failure. Preserve the phase and diagnostic instead of treating all three as a generic failed function. If a caller value unexpectedly changes, inspect whether the real signature uses a nonconst reference or pointer rather than the copied parameters shown here.
<!-- depth:end -->

## Worked example 1

```cpp
assert(clamp_reading(12, 0, 10) == 10);
```

Expected: 12 is above the upper bound, so the function returns 10.

## Worked example 2

```cpp
try {
  clamp_reading(5, 10, 0);
} catch (const std::invalid_argument &) { /* rejected */
}
```

Expected: The reversed interval raises invalid_argument before computing a result.

## Exercise 1: Predict the contract

Evaluate -3, 5, 12 for bounds [0, 10].

**Expected:** Results [0, 5, 10].

**Reasoning:** Below, inside and above are separate paths.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Check parameter isolation

Call with variable x=12 and inspect x afterward.

**Expected:** Result 10; caller x still 12.

**Reasoning:** Pass by value creates the parameter copy.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Build a predicate

Write inside(x, low, high) with inclusive bounds.

**Expected:** inside(0, 0, 10) true; inside(11, 0, 10) false.

**Reasoning:** Return a Boolean comparison conjunction.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair an invalid contract

Remove the reversed-bounds check and explain the lost guarantee.

**Expected:** clamp(5, 10, 0) must be rejected after repair.

**Reasoning:** min/max alone do not validate the meaning of the bounds.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check a one-point interval

Evaluate x=2, 3, 4 with bounds [3, 3].

**Expected:** All return 3.

**Reasoning:** Equal bounds form a valid single-value interval.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer to money

Clamp a cents amount of 1250 to [0, 1000].

**Expected:** 1000 integer cents, without floating conversion.

**Reasoning:** The contract applies to a different integer domain.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
