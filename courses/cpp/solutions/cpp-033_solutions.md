# cpp-033: explanations and reference observations

The [executable reference](cpp-033_solution.cpp) adds a baseline in which the atomic counter stays 0 when no thread increments it. The explanations cover promise ordering, repetition and keeping a deliberate race inside a scratch test. How to compare: [study guide](../STUDY-GUIDE.md#compare-with-the-solutions).

## Mechanism

A concurrent test must check results across meaningful interleavings. A schedule is an ordering of thread operations. Stress repeats a scenario but does not enumerate all schedules. ThreadSanitizer can detect many data races in an instrumented host run; it is a different tool from AddressSanitizer and usually requires a separate build.

## Detailed reasoning

A concurrency test must know which state it is waiting for. The readiness future observes one explicit worker event; join observes termination. The test repeats a fixed 200-increment invariant twenty times, which is useful bounded stress but does not enumerate all schedules. A separate supervisor deadline turns deadlock into a finite failure. TSan evidence requires an instrumented supported host run and should remain distinct from normal execution results.

<!-- depth:start -->
## Testing concurrency without guessing the schedule

A concurrency test needs observable synchronization points. A promise/future pair can signal that a worker reached a chosen state. join confirms that a worker has terminated. These facts are stronger than waiting an arbitrary number of milliseconds. A sleep changes the chance of an ordering but does not establish that the expected event happened.

In the first program, the worker assigns 42 and then fulfills a promise. Waiting on the future establishes the result's availability before main checks it. The worker is still joined to close its lifetime. Startup, publication and termination are separate events even when they occur close together in a tiny example.

The second program repeats a fixed invariant twenty times: two participants each increment the same atomic counter 100 times, and the joined result must be 200. Repetition can expose some timing-sensitive defects, but it does not enumerate all possible schedules. A passing stress loop is bounded evidence, not proof that a race is impossible. The synchronization argument remains necessary.

A supervisor timeout makes a deadlock or unresponsive worker a finite test failure. The timeout belongs outside the potentially stuck code path when necessary; a worker that never returns cannot reliably report its own timeout after the fact. Retain the phase, last observed synchronization point and cancellation outcome so the failure is diagnosable.

ThreadSanitizer is a separate instrumented execution path with toolchain and platform requirements. It can detect many data races in exercised code, but cannot prove all schedules or all code paths safe. Normal execution, stress repetition and sanitizer reports should be recorded separately. Do not add an intentional race to the ordinary browser source and then interpret one successful run as a detector test.

## Debugging the contract

If a test flakes under load, replace timing assumptions with explicit state signals. If it hangs, identify the last completed promise/condition/join boundary and use the external timeout receipt. If a stress test passes a deliberately racy mutation, that shows limited schedule coverage rather than correctness. If TSan is unavailable on a platform, leave that row unqualified instead of treating the normal binary as equivalent instrumentation.
<!-- depth:end -->

## Worked example 1

```cpp
ready.set_value(); // owner waits on ready.get_future().get()
```

Expected: The owner receives explicit evidence that the worker reached the named phase.

## Worked example 2

```cpp
t.join();
assert(count == 200);
```

Expected: Two sets of 100 atomic increments must total 200 in each trial.

## Exercise 1: Identify the schedule point

Name the purpose of the ready handshake.

**Expected:** It proves worker startup, not worker completion.

**Reasoning:** join remains necessary for the final assertion.

**Verify:** Check your answer against Worked example 1: `started.get()` returns only after `ready.set_value()`, and `worker.join()` is still needed before the program ends.

## Exercise 2: Run bounded stress

Repeat the 200-count scenario 20 times.

**Expected:** 20 exact invariant passes, no sleeps.

**Reasoning:** A finite repetition count gives a declared work budget.

**Verify:** Confirm Worked example 2 runs 20 trials, asserts `count == 200` in every trial and never sleeps.

## Exercise 3: Add a timeout contract

Wrap the host test process in a finite supervisor deadline.

**Expected:** A deadlock is reported as timeout rather than hanging indefinitely.

**Reasoning:** The timeout belongs outside potentially deadlocked worker code.

**Verify:** Run a deliberately deadlocked scratch copy under `timeout 10` (or `ctest --timeout 10`) and confirm a timeout result, status 124 from `timeout`, instead of a hang.

## Exercise 4: Repair timing assumptions

Replace a fixed sleep used to infer startup with a promise.

**Expected:** Test proceeds only after the readiness event.

**Reasoning:** Wall-clock delay cannot prove a state transition.

**Verify:** Confirm the repaired test calls `set_value()` in the worker and `get()` on the matching future before the main thread continues, and that no `sleep_for` remains.

## Exercise 5: Qualify TSan separately

Use an existing supported compiler with -fsanitize=thread on an owned host copy.

**Expected:** Actual build/run receipt or explicit unavailable status.

**Reasoning:** The browser normal profile does not claim TSan coverage.

**Verify:** Record the exact compile command, its status and the run status, or write unavailable with the compiler's error message if it rejects `-fsanitize=thread`.

## Exercise 6: Transfer negative control

Introduce a plain counter race only in a separately instrumented scratch test.

**Expected:** TSan finding expected; production example stays race-free.

**Reasoning:** A clean correct example alone does not demonstrate detector sensitivity.

**Verify:** Confirm the ThreadSanitizer report names a data race on the plain counter in the scratch file, then rebuild Worked example 2 with the same flags and confirm it reports nothing.
