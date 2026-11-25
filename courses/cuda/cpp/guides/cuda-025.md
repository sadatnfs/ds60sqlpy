# cuda-025: A disciplined CUDA error taxonomy

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-012`, `cuda-013`, `cuda-014`, `cuda-024`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Classify a CUDA failure by its phase and write a bug report around the smallest reproducer.

**Scope:** Compilation, linking, loading, invalid launch, allocation, asynchronous execution and application-validation failures.

**Evidence to produce:** A useful bug report that includes the smallest reproducer and the responsible phase.

## Purpose, vocabulary and mental model

Debugging starts by placing a failure in its phase. A source error prevents compilation; a missing symbol prevents linking; incompatible device code can prevent loading; invalid launch parameters can reject submission; an illegal access can fail asynchronous execution; and a completed kernel can still calculate the wrong answer. Later CUDA calls may surface an earlier asynchronous failure, so the line reporting an error is not always the line that caused it. Use checked phase boundaries in a debug configuration and retain the earliest meaningful diagnostic. Avoid reinstalling tools before a small reproducer isolates the responsible layer.

### Key terms

- **Sticky error:** An asynchronous device fault, such as an illegal address, that corrupts the context so later CUDA calls keep failing.
- **Non-sticky error:** An error such as an invalid launch configuration that is reported once and leaves the context usable.
- **cudaGetLastError:** A runtime call that returns the most recent error and resets non-sticky errors, commonly used right after a launch.
- **Minimal reproducer:** The smallest program and input that still show a failure, with unrelated work removed.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-025_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-025_cpu.py
```

## Worked example 1: trace the mechanism

A misspelled identifier in main.cu produces a compiler error before any device work. Fixing bounds checks cannot help until the file compiles. Record the diagnostic with source line and build command, and rerun the smallest compilation step.

**Why:** No device code exists until compilation succeeds, so runtime checks are irrelevant.

```python
failures = {
    "unknown identifier": "compile",
    "undefined reference": "link",
    "illegal access at completion": "execute",
    "wrong sum": "validate",
}
assert failures["wrong sum"] == "validate"
assert failures["unknown identifier"] != failures["illegal access at completion"]
print(failures)
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'unknown identifier': 'compile', 'undefined reference': 'link', 'illegal access at completion': 'execute', 'wrong sum': 'validate'}
```

**Check:** Rerun only the compile command for main.cu and confirm it exits zero.

## Worked example 2: change a meaningful condition

A launch is accepted but a checked synchronization reports an illegal memory access. Now examine ownership and bounds near that launch. If synchronization succeeds and one output is wrong, inspect arithmetic, layout or uninitialized data instead. These outcomes require different next experiments.

**Why:** Launch acceptance only means the configuration was valid; the fault appears when work completes.

**Check:** Check indices near that kernel's bounds and rerun with a sanitizer to name the bad address.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Classify the misspelled identifier as a compile failure and fix it at the reported source line.

**Trap to avoid:** Adding bounds checks in the kernel cannot help a file that never builds.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Treat an illegal access at a checked synchronization as an execution failure tied to the preceding launch.

**Trap to avoid:** Blaming the synchronize call itself sends you to inspect the wrong line of host code.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Classify an undefined reference to a host helper.

**Trap to avoid:** Recompiling with different GPU architecture flags changes nothing about a missing host symbol.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why add synchronization after each stage only during localization?

**Trap to avoid:** Leaving every synchronization in production serializes stages that could overlap.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does a no-device status mean for a numerical test?

**Trap to avoid:** Counting it as passed hides that the GPU path has never been exercised.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Write a minimal bug report for a shape-dependent wrong answer.

**Trap to avoid:** Writing only 'wrong answer on large inputs' gives no reproducer and no index to inspect.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Every error is fixed by reinstalling CUDA or rebuilding every image.** Reinstalling only changes the toolkit and driver, which matters for loading or version failures but not for code faults. A compile error needs a source fix, an illegal access needs bounds or ownership repair, and a wrong answer after a clean run needs arithmetic or layout review. Classifying the phase first, as worked examples 1 and 2 do, tells you which repair applies and avoids hours of unrelated rebuilds.

## Self-check, retrieval and transfer

1. Why can an error appear at a line far from the faulty kernel?
2. What is a sticky error?
3. What should a minimal reproducer contain?

Short answers are in the [separate explanations](../solutions/cuda-025_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-025: A disciplined CUDA error taxonomy.
Read courses/cuda/cpp/guides/cuda-025.md and courses/cuda/cpp/lessons/cuda-025.md.
Direct prerequisites: `cuda-012`, `cuda-013`, `cuda-014`, `cuda-024`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-025_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-025_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
