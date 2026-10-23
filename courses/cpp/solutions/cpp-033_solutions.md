# cpp-033: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A concurrent test must check results across meaningful interleavings. A schedule is an ordering of thread operations. Stress repeats a scenario but does not enumerate all schedules. ThreadSanitizer can detect many data races in an instrumented host run; it is a different tool from AddressSanitizer and usually requires a separate build.

## Detailed reasoning

A concurrency test must know which state it is waiting for. The readiness future observes one explicit worker event; join observes termination. The test repeats a fixed 200-increment invariant twenty times, which is useful bounded stress but does not enumerate all schedules. A separate supervisor deadline turns deadlock into a finite failure. TSan evidence requires an instrumented supported host run and should remain distinct from normal execution results.

## Worked example 1

```cpp
ready.set_value(); // owner waits on ready.get_future().get()
```

Expected: The owner receives explicit evidence that the worker reached the named phase.

## Worked example 2

```cpp
t.join(); assert(count==200);
```

Expected: Two sets of 100 atomic increments must total 200 in each trial.

## Exercise 1: Identify the schedule point

Name the purpose of the ready handshake.

**Expected:** It proves worker startup, not worker completion.

**Reasoning:** join remains necessary for the final assertion.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Run bounded stress

Repeat the 200-count scenario 20 times.

**Expected:** 20 exact invariant passes, no sleeps.

**Reasoning:** A finite repetition count gives a declared work budget.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Add a timeout contract

Wrap the host test process in a finite supervisor deadline.

**Expected:** A deadlock is reported as timeout rather than hanging indefinitely.

**Reasoning:** The timeout belongs outside potentially deadlocked worker code.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair timing assumptions

Replace a fixed sleep used to infer startup with a promise.

**Expected:** Test proceeds only after the readiness event.

**Reasoning:** Wall-clock delay cannot prove a state transition.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Qualify TSan separately

Use an existing supported compiler with -fsanitize=thread on an owned host copy.

**Expected:** Actual build/run receipt or explicit unavailable status.

**Reasoning:** The browser normal profile does not claim TSan coverage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer negative control

Introduce a plain counter race only in a separately instrumented scratch test.

**Expected:** TSan finding expected; production example stays race-free.

**Reasoning:** A clean correct example alone does not demonstrate detector sensitivity.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.
