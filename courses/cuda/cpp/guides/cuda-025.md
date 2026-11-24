# cuda-025: A disciplined CUDA error taxonomy

## Level and prerequisites

Intermediate; about 110 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-012`, `cuda-013`, `cuda-014`, `cuda-024`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Classify a CUDA failure by its phase and write a bug report around the smallest reproducer.

Work through *A disciplined CUDA error taxonomy* with the concrete cases below. Finish with this evidence:
a useful bug report that includes the smallest reproducer and the responsible phase. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Debugging starts by placing a failure in its phase. A source error prevents compilation; a missing symbol prevents linking; incompatible device code can prevent loading; invalid launch parameters can reject submission; an illegal access can fail asynchronous execution; and a completed kernel can still calculate the wrong answer. Later CUDA calls may surface an earlier asynchronous failure, so the line reporting an error is not always the line that caused it. Use checked phase boundaries in a debug configuration and retain the earliest meaningful diagnostic. Avoid reinstalling tools before a small reproducer isolates the responsible layer.

### Key terms

- **Sticky error:** An asynchronous device fault, such as an illegal address, that corrupts the context so later CUDA calls keep failing.
- **Non-sticky error:** An error such as an invalid launch configuration that is reported once and leaves the context usable.
- **cudaGetLastError:** A runtime call that returns the most recent error and resets non-sticky errors, commonly used right after a launch.
- **Minimal reproducer:** The smallest program and input that still show a failure, with unrelated work removed.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-025_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-025_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A misspelled identifier in main.cu produces a compiler error before any device work. Fixing bounds checks cannot help until the file compiles. Record the diagnostic with source line and build command, and rerun the smallest compilation step.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

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

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'unknown identifier': 'compile', 'undefined reference': 'link', 'illegal access at completion': 'execute', 'wrong sum': 'validate'}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A launch is accepted but a checked synchronization reports an illegal memory access. Now examine ownership and bounds near that launch. If synchronization succeeds and one output is wrong, inspect arithmetic, layout or uninitialized data instead. These outcomes require different next experiments.

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

Classify an undefined reference to a host helper.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why add synchronization after each stage only during localization?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does a no-device status mean for a numerical test?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Write a minimal bug report for a shape-dependent wrong answer.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **every error is fixed by reinstalling CUDA or rebuilding every image.**

For the concrete failure exercise, why add synchronization after each stage only during localization?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-025_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

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
