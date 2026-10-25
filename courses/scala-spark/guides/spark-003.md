# spark-003: Functions, arguments, and explicit return contracts

Authored classroom lesson. Content availability and runtime readiness are separate checks. Read the current capability notice before running. No opening or saving this lesson installs tools, starts a cluster or proves mastery.

## Level and prerequisites

Beginner; 60 minutes. Direct design prerequisites: `spark-002`. Use the subject browser to open prerequisite lessons or review their concepts. Runtime readiness is checked separately before execution.

Learner artifact: [spark-003.scala](../lessons/spark-003.scala). Keep [solutions](../solutions/spark-003_solutions.md) closed until an attempt or explicit reveal.

## Learning objectives

- Write small pure Scala functions with named inputs and explicit return types.
- Produce the exact bounded evidence named by the six exercises and explain one counterexample.

## Vocabulary and concepts

A function names a rule with input parameters and a result type. `def addCents(left: Long, right: Long): Long = left + right` reads: accept two Long values, return a Long, and evaluate their sum. Calling it supplies argument values; defining it does not run it. A pure function has no hidden state change and returns the same answer for the same inputs. An explicit return type makes the contract visible to both the reader and compiler.

The fee domain is deliberately bounded to amounts from-1000000 through1000000 cents. Nonpositive amounts cost zero. A nonmember with a positive amount pays20 cents. A member pays zero below500 cents and five percent at or above500, rounded down by integer division. This makes every branch and numeric boundary inspectable. Multiplication is safe inside this domain; the lesson does not promise arbitrary Long multiplication cannot overflow.

- **def:** introduces a named function
- **parameter:** a named input inside the definition
- **argument:** a value supplied in a call
- **Boolean:** true or false, used by the branch
- **pure function:** a repeatable input-to-result rule with no externally visible mutation

## Worked example / walkthrough

### Worked example 1: Call a function twice

Arguments vary while the rule remains fixed. Assertions state the return contract.

```scala
def addCents(a: Long, b: Long): Long = a + b
assert(addCents(30L, 5L) == 35L)
assert(addCents(0L, 5L) == 5L)
```

**Expected:** 35L and5L, from the same function definition.

### Worked example 2: Make a total bounded branch

The equality boundary belongs to one branch deliberately; testing only20 would miss it.

```scala
def bonus(points: Long): Long = if (points >= 10L) 2L else 0L
assert(bonus(9L) == 0L)
assert(bonus(10L) == 2L)
```

**Expected:** 9 maps to0L and10 maps to2L.

## Exercises

### Exercise 1: Separate definition and call

Explain addCents then evaluate two calls.

**Inputs/evidence:** For spark-003 Exercise 1, addCents(100L,25L),addCents(0L,25L).

**Expected result/shape:** For spark-003 Exercise 1, 125L and25L.

**Verify:** For spark-003 Exercise 1, assert both returned values; distinguish parameter names from arguments.

**Progressive hints:**

1. Find the function name.
2. Substitute each argument into its parameter.
3. Return the expression, not its printed representation.

### Exercise 2: Implement branch order

Implement the fee rule with the nonpositive guard first.

**Inputs/evidence:** For spark-003 Exercise 2, 0L with both membership values;100L with both values.

**Expected result/shape:** For spark-003 Exercise 2, fees0/0 for zero and0/20 for100.

**Verify:** For spark-003 Exercise 2, assert all four cases and inspect guard order.

**Progressive hints:**

1. Find the shared exception to all fees.
2. Nonpositive amounts are handled before membership.
3. Start if(amount<=0L)0L.

### Exercise 3: Test the membership threshold

Cover just below, exactly at and just above500.

**Inputs/evidence:** For spark-003 Exercise 3, member499L,500L,501L.

**Expected result/shape:** For spark-003 Exercise 3, fees0L,25L,25L.

**Verify:** For spark-003 Exercise 3, assert the exact three outputs and explain integer division.

**Progressive hints:**

1. The equality case matters.
2. Long division discards the fractional remainder.
3. Use amount<500L for the free member branch.

### Exercise 4: Use named arguments

Call the same function with named parameters in reverse order.

**Inputs/evidence:** For spark-003 Exercise 4, feeCents(isMember=true,amount=1000L).

**Expected result/shape:** For spark-003 Exercise 4, 50L, equal to the positional call.

**Verify:** For spark-003 Exercise 4, assert both calls give50L; do not change the definition.

**Progressive hints:**

1. Read names rather than position.
2. Both calls supply the same two values.
3. Keep amount and isMember names exact.

### Exercise 5: Reject hidden state

Compare a proposed call counter with the fee contract.

**Inputs/evidence:** For spark-003 Exercise 5, two consecutive feeCents(1000L,true) calls and negative amount-1L.

**Expected result/shape:** For spark-003 Exercise 5, both calls50L; negative amount yields0L even for a nonmember.

**Verify:** For spark-003 Exercise 5, repeat exact calls and explain why a call counter must not alter the returned fee.

**Progressive hints:**

1. Does history belong in this input contract?
2. Same inputs must preserve the fee.
3. Return50L both times, and guard the negative boundary.

### Exercise 6: Transfer and explain the domain

Predict member2000L and nonmember2000L; review an out-of-domain value.

**Inputs/evidence:** For spark-003 Exercise 6, 2000L,true/false and2000000L.

**Expected result/shape:** For spark-003 Exercise 6, 100L/20L; the out-of-domain input is rejected by the reference precondition.

**Verify:** For spark-003 Exercise 6, assert the two valid results and identify the violated bound for the third.

**Progressive hints:**

1. Reapply the same rule.
2. A flat fee does not grow with the amount.
3. 2000*5/100=100;2000000 exceeds the declared limit.

## Self-check

- Can you reproduce each exact observation without reading the official answer?
- Can you explain a failed check using the lesson's model, rather than changing an expected value?

## Retrieval and transfer

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

## Common pitfalls

Returning println(...) gives Unit, not Long. Checking membership before a zero/negative guard changes the policy. Multiplying arbitrary Long values can overflow, so preserve the declared domain rather than extrapolating from tiny fixtures. The learner stub intentionally fails until feeCents is implemented.

## Next step

Continue to [spark-004](spark-004.md) for immutable collections and transformations. Review the [course README](../README.md) and retain your boundary table.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach spark-003.
Read courses/scala-spark/guides/spark-003.md and courses/scala-spark/lessons/spark-003.scala.
Direct design prerequisites: `spark-002`. This lesson is authored; check its current runtime readiness and direct prerequisites.
Explain one mechanism, ask me to predict, let me attempt one exercise, then give one hint at a time.
Do not read courses/scala-spark/solutions/ until I make an honest attempt or explicitly ask for a reveal.
Review my exact values, diagnostics or written evidence; distinguish source inspection, process success and verified understanding.
Finish with a changed fixture and retrieval in my own words. Do not install tools, download assets or select an ambient cluster for me.
```
