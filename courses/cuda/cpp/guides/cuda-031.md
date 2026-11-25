# cuda-031: Timing asynchronous work correctly

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-007`, `cuda-008`, `cuda-014`, `cuda-024`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Measure asynchronous GPU work with CUDA events and report the sample distribution beside a CPU baseline.

**Scope:** Host clocks, device events, synchronization boundaries, warm-up, JIT costs, repetitions, variance and timing scope.

**Evidence to produce:** Raw samples, a reported distribution and an honest comparison with CPU execution.

## Purpose, vocabulary and mental model

A host clock around an asynchronous launch measures submission unless a completion dependency is included. Device events record positions in a stream and can measure elapsed device work between those positions after completion. End-to-end host timing includes the transfers and synchronization the application actually requires. Warm-up separates one-time initialization or JIT work from repeated work, but cold start remains a real user concern and deserves its own measurement. Retain repeated samples and summarize a distribution. Profiling or sanitizer instrumentation changes execution, so do not mix instrumented and ordinary samples in one performance claim.

### Key terms

- **CUDA event:** A marker recorded in a stream whose completion can be queried or used to compute elapsed device time.
- **cudaEventElapsedTime:** A call that returns the milliseconds between two completed events.
- **End-to-end time:** Host-observed time that includes the transfers, synchronization and launches the application needs.
- **Cold start:** The first execution, which includes one-time costs such as context creation, module loading or JIT.

## Mathematical contract

\[
S=\frac{T_{\mathrm{baseline}}}{T_{\mathrm{candidate}}}
\]

Both durations must measure the same input, result and timing scope. A ratio of host request time to isolated kernel time compares different contracts.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-031_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-031_cpu.py
```

## Worked example 1: trace the mechanism

Suppose host submission takes 5 microseconds and the queued kernel completes 80 microseconds later. Reporting five as kernel duration measures the wrong interval. A correctly ordered event interval measures relevant device work; a completed host interval can measure the full request, including additional overhead.

**Why:** The 5 microseconds is host submission; the kernel completes 80 microseconds later.

```python
import statistics

samples = [1.0, 1.1, 1.0, 1.2, 9.0]
assert statistics.median(samples) == 1.1
print(
    {
        "synthetic_samples_ms": samples,
        "median_ms": statistics.median(samples),
        "maximum_ms": max(samples),
    }
)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'synthetic_samples_ms': [1.0, 1.1, 1.0, 1.2, 9.0], 'median_ms': 1.1, 'maximum_ms': 9.0}
```

**Check:** Compare the event interval with a synchronized host interval and explain the gap.

## Worked example 2: change a meaningful condition

Samples \([1.0,1.1,1.0,1.2,9.0]\) milliseconds have median 1.1, but the 9.0 sample still matters. Retain it and investigate interference or cold behavior instead of deleting it merely because it weakens a speedup. Report the warm-up rule before collecting data.

**Why:** The median resists one outlier, but the outlier may reveal interference or cold start.

**Check:** The reference asserts statistics.median(samples) == 1.1.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Time device work with events recorded in the same stream around the kernel.

**Trap to avoid:** Wrapping only the launch call in a host timer reports submission, not execution.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Report median 1.1 ms and keep the 9.0 ms maximum with a warm-up rule.

**Trap to avoid:** Deleting 9.0 because it hurts the speedup removes real evidence after the fact.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute speedup for matching end-to-end times 12 ms and 4 ms.

**Trap to avoid:** Using kernel-only time for the GPU side inflates the speedup.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A benchmark starts an event in one stream and ends it in an unrelated stream. What is missing?

**Trap to avoid:** Assuming streams run in launch order gives an interval with no defined meaning.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How do you time an empty operation?

**Trap to avoid:** Reporting near-infinite items per second from an empty run misleads readers.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Compare resident-data and request-response workloads.

**Trap to avoid:** Excluding transfers from request-response timing measures work the caller never sees alone.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Measuring the launch call measures the GPU's work or excluding transfers is always representative.** A host clock around a launch measures submission, not execution, as worked example 1 shows with 5 microseconds reported for 80 microseconds of work. Excluding transfers is representative only when the data truly stays resident; a request-response service pays the upload and download on every call, so its timing must include them.

## Self-check, retrieval and transfer

1. What must happen before reading an elapsed time between two events?
2. Why keep the 9.0 ms sample in worked example 2?
3. What does warm-up separate from repeated work?

Short answers are in the [separate explanations](../solutions/cuda-031_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-031: Timing asynchronous work correctly.
Read courses/cuda/cpp/guides/cuda-031.md and courses/cuda/cpp/lessons/cuda-031.md.
Direct prerequisites: `cuda-007`, `cuda-008`, `cuda-014`, `cuda-024`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-031_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-031_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
