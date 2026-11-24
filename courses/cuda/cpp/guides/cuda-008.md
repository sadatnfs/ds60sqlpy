# cuda-008: Reproducibility, safety and the first evidence notebook

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-003`, `cuda-006`, `cuda-007`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Create a reusable experiment template that records inputs, environment, timing scope and capability status.

Work through *Reproducibility, safety and the first evidence notebook* with the concrete cases below. Finish with this evidence:
a reusable experiment template and correctly labeled capability status. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A reproducible experiment records enough context to explain why a result happened. An input seed is useful only alongside the generator, dtype, shape and distribution. A benchmark needs timing scope, warm-up policy and retained samples, while a correctness result needs an independent expected answer. Hardware access, successful compilation, successful execution and acceptable numerical output are four distinct observations. A resource budget limits input size and repeated work before running. On a shared GPU, reserve only the memory and compute time that the owner has authorized; do not use unbounded spin loops as teaching fixtures.

### Key terms

- **Random seed:** The initial value for a pseudorandom generator, meaningful only together with the generator, dtype, shape and distribution.
- **Warm-up run:** An untimed execution that absorbs one-time initialization or JIT costs before repeated measurements.
- **Timing scope:** The exact set of operations, such as kernel only or end to end, that a measurement includes.
- **Capability status:** A labeled record of which observations exist, such as compiled, executed on a GPU or validated numerically.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-008_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-008_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

Report A says 'GPU: 0.2 ms'. Report B records a synthetic float32 vector of 1,024 elements, seed 7, upload excluded, five warm-ups, twenty event-timed samples, device/toolkit identities and an absolute error bound. B is interpretable, but it still needs raw samples and CPU comparison before supporting a speedup claim.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
x, y = [0, -2, 5], [3, 2, -1]
assert [a + b for a, b in zip(x, y)] == [3, 0, 4]
receipt = {"surface": "CPU reference", "shape": [3], "result": [3, 0, 4], "gpu_executed": False}
print(receipt)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'surface': 'CPU reference', 'shape': [3], 'result': [3, 0, 4], 'gpu_executed': False}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A vector-add oracle uses \([0,-2,5]\) and \([3,2,-1]\), expecting \([3,0,4]\). Add length-zero and a 33-element fixture to expose assumptions about block boundaries. This reference can run on any CPU. Label it CPU correctness evidence rather than evidence that a GPU kernel has run.

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

Write five required fields for a correctness receipt.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A run was cancelled but marked passed because the compiler exited zero. Correct the record.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

How should a no-device run be represented?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a memory budget for three float32 vectors of one million elements.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a screenshot of a timing or a driver version is sufficient runtime evidence.**

For the concrete failure exercise, a run was cancelled but marked passed because the compiler exited zero. Correct the record.
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-008_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-008: Reproducibility, safety and the first evidence notebook.
Read courses/cuda/cpp/guides/cuda-008.md and courses/cuda/cpp/lessons/cuda-008.md.
Direct prerequisites: `cuda-003`, `cuda-006`, `cuda-007`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-008_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-008_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
