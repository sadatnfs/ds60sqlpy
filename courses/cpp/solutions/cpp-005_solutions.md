# cpp-005: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A function names a computation with parameters as inputs and a return value as its output. A precondition is a promise the caller must satisfy. A postcondition describes the result. Pure functions avoid hidden state, so the same inputs produce the same value and small boundary tests are meaningful.

## Detailed reasoning

A caller has three distinct questions: are the bounds valid, is the value below/inside/above them, and may the call alter its input? The supplied function rejects reversed bounds first. Only then does it compute min(value,high), followed by max(low,...). The three ordinary cases cover each position relative to the interval, while equal bounds test a degenerate but valid interval. A return value can differ from the argument without mutating the caller because parameters are copies.

## Worked example 1

```cpp
assert(clamp_reading(12,0,10)==10);
```

Expected: 12 is above the upper bound, so the function returns 10.

## Worked example 2

```cpp
try { clamp_reading(5,10,0); } catch(const std::invalid_argument&) { /* rejected */ }
```

Expected: The reversed interval raises invalid_argument before computing a result.

## Exercise 1: Predict the contract

Evaluate -3,5,12 for bounds [0,10].

**Expected:** Results [0,5,10].

**Reasoning:** Below, inside and above are separate paths.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Check parameter isolation

Call with variable x=12 and inspect x afterward.

**Expected:** Result 10; caller x still 12.

**Reasoning:** Pass by value creates the parameter copy.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Build a predicate

Write inside(x,low,high) with inclusive bounds.

**Expected:** inside(0,0,10) true; inside(11,0,10) false.

**Reasoning:** Return a Boolean comparison conjunction.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair an invalid contract

Remove the reversed-bounds check and explain the lost guarantee.

**Expected:** clamp(5,10,0) must be rejected after repair.

**Reasoning:** min/max alone do not validate the meaning of the bounds.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check a one-point interval

Evaluate x=2,3,4 with bounds [3,3].

**Expected:** All return 3.

**Reasoning:** Equal bounds form a valid single-value interval.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer to money

Clamp a cents amount of 1250 to [0,1000].

**Expected:** 1000 integer cents, without floating conversion.

**Reasoning:** The contract applies to a different integer domain.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
