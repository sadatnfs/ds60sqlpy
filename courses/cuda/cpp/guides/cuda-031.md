# cuda-031: Timing asynchronous work correctly

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-007`, `cuda-008`, `cuda-014`, `cuda-024`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Measure asynchronous GPU work with CUDA events and report the sample distribution beside a CPU baseline.

Work through *Timing asynchronous work correctly* with the concrete cases below. Finish with this evidence:
raw samples, a reported distribution and an honest comparison with CPU execution. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

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

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-031_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-031_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Suppose host submission takes 5 microseconds and the queued kernel completes 80 microseconds later. Reporting five as kernel duration measures the wrong interval. A correctly ordered event interval measures relevant device work; a completed host interval can measure the full request, including additional overhead.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

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

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'synthetic_samples_ms': [1.0, 1.1, 1.0, 1.2, 9.0], 'median_ms': 1.1, 'maximum_ms': 9.0}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Samples \([1.0,1.1,1.0,1.2,9.0]\) milliseconds have median 1.1, but the 9.0 sample still matters. Retain it and investigate interference or cold behavior instead of deleting it merely because it weakens a speedup. Report the warm-up rule before collecting data.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

Exercises 1 and 2 are guided reconstructions of the worked examples; exercises
3-6 change an input, diagnose a defect, test a boundary and transfer the idea.
For each one, keep the calculation, output, diagram or failure policy you
produce so another reader can compare it with the worked cases. If the hint is
not enough, reread the mechanism paragraph and the bounded CPU assertion.

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Compute speedup for matching end-to-end times 12 ms and 4 ms.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A benchmark starts an event in one stream and ends it in an unrelated stream. What is missing?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How do you time an empty operation?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Compare resident-data and request-response workloads.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **measuring the launch call measures the GPU's work or excluding transfers is always representative.**

For the concrete failure exercise, a benchmark starts an event in one stream and ends it in an unrelated stream. What is missing?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-031_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
