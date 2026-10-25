# cuda-031: Timing asynchronous work correctly

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-007`, `cuda-008`, `cuda-014`, `cuda-024`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain timing asynchronous work correctly using the concrete cases below. Produce raw samples, a reported distribution and an honest comparison with CPU execution.
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

A host clock around an asynchronous launch measures submission unless a completion dependency is included. Device events record positions in a stream and can measure elapsed device work between those positions after completion. End-to-end host timing includes the transfers and synchronization the application actually requires. Warm-up separates one-time initialization or JIT work from repeated work, but cold start remains a real user concern and deserves its own measurement. Retain repeated samples and summarize a distribution. Profiling or sanitizer instrumentation changes execution, so do not mix instrumented and ordinary samples in one performance claim.

## Mathematical contract

\[
S=\frac{T_{\mathrm{baseline}}}{T_{\mathrm{candidate}}}
\]

Both durations must measure the same input, result and timing scope. A ratio of host request time to isolated kernel time compares different contracts.

## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/cuda-031_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python courses/cuda/cpp/references/cuda-031_cpu.py
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

Suppose host submission takes 5 microseconds and the queued kernel completes 80 microseconds later. Reporting five as kernel duration measures the wrong interval. A correctly ordered event interval measures relevant device work; a completed host interval can measure the full request, including additional overhead.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
import statistics

samples = [1.0, 1.1, 1.0, 1.2, 9.0]
assert statistics.median(samples) == 1.1
assert 12 / 4 == 3
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

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

Samples \([1.0,1.1,1.0,1.2,9.0]\) milliseconds have median 1.1, but the 9.0 sample still matters. Retain it and investigate interference or cold behavior instead of deleting it merely because it weakens a speedup. Report the warm-up rule before collecting data.

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

## Six progressive exercises

### Exercise 1

Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Start with the literal input and intermediate quantities in worked example 1.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 2

Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Identify exactly which condition changes in worked example 2.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 3

Compute speedup for matching end-to-end times 12 ms and 4 ms.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Use the first worked example to establish the relevant quantities, then change only the requested input.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 4

A benchmark starts an event in one stream and ends it in an unrelated stream. What is missing?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Locate the failed phase or violated dependency before proposing a repair.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 5

How do you time an empty operation?

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** Check what the algorithm is allowed to read, write or assume at this boundary.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

### Exercise 6

Compare resident-data and request-response workloads.

**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.

**Hint 1:** State the output contract and which observations are needed in the new application.

**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **measuring the launch call measures the GPU's work or excluding transfers is always representative.**

For the concrete failure exercise, a benchmark starts an event in one stream and ends it in an unrelated stream. What is missing?
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-031_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

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
