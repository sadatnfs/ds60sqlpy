# cuda-031: explanatory solutions

## Mechanism review

A host clock around an asynchronous launch measures submission unless a completion dependency is included. Device events record positions in a stream and can measure elapsed device work between those positions after completion. End-to-end host timing includes the transfers and synchronization the application actually requires. Warm-up separates one-time initialization or JIT work from repeated work, but cold start remains a real user concern and deserves its own measurement. Retain repeated samples and summarize a distribution. Profiling or sanitizer instrumentation changes execution, so do not mix instrumented and ordinary samples in one performance claim.

## Exercise 1

Suppose host submission takes 5 microseconds and the queued kernel completes 80 microseconds later. Reporting five as kernel duration measures the wrong interval. A correctly ordered event interval measures relevant device work; a completed host interval can measure the full request, including additional overhead.

**Approach:** Time device work with events recorded in the same stream around the kernel.

**Why it is correct:** The 5 microseconds is host submission; the kernel completes 80 microseconds later.

**A plausible wrong approach:** Wrapping only the launch call in a host timer reports submission, not execution.

**How to verify:** Compare the event interval with a synchronized host interval and explain the gap.

## Exercise 2

Samples \([1.0,1.1,1.0,1.2,9.0]\) milliseconds have median 1.1, but the 9.0 sample still matters. Retain it and investigate interference or cold behavior instead of deleting it merely because it weakens a speedup. Report the warm-up rule before collecting data.

**Approach:** Report median 1.1 ms and keep the 9.0 ms maximum with a warm-up rule.

**Why it is correct:** The median resists one outlier, but the outlier may reveal interference or cold start.

**A plausible wrong approach:** Deleting 9.0 because it hurts the speedup removes real evidence after the fact.

**How to verify:** The reference asserts statistics.median(samples) == 1.1.

## Exercise 3

Three times. Do not substitute an isolated kernel time into one side of that comparison.

**Approach:** Divide 12 ms by 4 ms using matching end-to-end scopes.

**Why it is correct:** Equal scopes make the ratio 3 a statement about the same work.

**A plausible wrong approach:** Using kernel-only time for the GPU side inflates the speedup.

**How to verify:** The reference asserts 12 / 4 == 3.

## Exercise 4

A defined ordering/dependency and timing scope. Unordered stream positions do not establish the intended interval.

**Approach:** Record both events in one stream or add an explicit dependency between streams.

**Why it is correct:** Events only bracket work they are ordered with.

**A plausible wrong approach:** Assuming streams run in launch order gives an interval with no defined meaning.

**How to verify:** Check the interval is stable across runs and covers the intended kernels.

## Exercise 5

Report fixed overhead separately and avoid interpreting division by near-zero work as meaningful throughput.

**Approach:** Report the fixed overhead as a time and skip throughput for zero work.

**Why it is correct:** Dividing zero items by a small time is not throughput.

**A plausible wrong approach:** Reporting near-infinite items per second from an empty run misleads readers.

**How to verify:** Assert the empty case reports overhead only.

## Exercise 6

Resident data can exclude repeated uploads by contract; request-response timing must include transfers needed to deliver the requested result.

**Approach:** Exclude uploads only when data truly stays resident; include them for request-response.

**Why it is correct:** Each workload's timing should match what a user must wait for.

**A plausible wrong approach:** Excluding transfers from request-response timing measures work the caller never sees alone.

**How to verify:** State each scope next to its number and confirm transfers are included where needed.

## Self-check answers

1. **What must happen before reading an elapsed time between two events?** The end event must complete, typically by synchronizing on it.
2. **Why keep the 9.0 ms sample in worked example 2?** It may reveal interference or cold behavior that real users would also see.
3. **What does warm-up separate from repeated work?** One-time costs such as context creation, module loading and JIT compilation.

## Numerical reference and its limits

The [CPU reference](../references/cuda-031_cpu.py) reproduces worked example 1 and prints `{'synthetic_samples_ms': [1.0, 1.1, 1.0, 1.2, 9.0], 'median_ms': 1.1, 'maximum_ms': 9.0}`.

It also asserts an exercise answer you derive yourself: `assert 12 / 4 == 3`

## Transfer review

Resident data can exclude repeated uploads by contract; request-response timing must include transfers needed to deliver the requested result.
