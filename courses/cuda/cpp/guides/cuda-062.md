# cuda-062: Portability, operations and the cost of a GPU dependency

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-003`, `cuda-008`, `cuda-030`, `cuda-061`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *Portability, operations and the cost of a GPU dependency* with the concrete cases below. Finish with this evidence:
a deployment checklist tied to supported evidence tiers and graceful failures. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

Portability means defining what is supported and how unsupported situations behave. CUDA execution requires a supported NVIDIA device and host software path; a CPU-only classroom can still teach algorithms and validate CPU references. AMD, Intel and Apple GPU programming use different backends and APIs, not an automatic CUDA compatibility promise. Detect capability for the operation, not simply the operating-system name. Containers package user-space dependencies but share host driver and hardware constraints. MIG, MPS, device sharing and resets are operator-managed topics. A teaching worker must never silently reset a shared device or erase learner state to recover from a fault.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-062_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-062_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A dispatch policy offers CPU reference on every ordinary classroom and CUDA execution only after visibility, allocation and a small numerical probe succeed. It records which path actually ran. The same expected mathematical result does not make CPU output evidence of CUDA execution.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
capability = {"reading": True, "CPU_reference": True, "CUDA_device_probe": False}
selected = "CUDA" if capability["CUDA_device_probe"] else "CPU_reference"
assert selected == "CPU_reference"
print({"selected_path": selected, "CUDA_execution": "unavailable"})
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'selected_path': 'CPU_reference', 'CUDA_execution': 'unavailable'}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A model fits on one 24 GiB GPU but fails on an 8 GiB device. The container tag is identical; the resource contract is not. Reduce the bounded workload or choose a supported alternate path, preserving the original memory error and learner source.

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

Write a supported-surface table for Linux, WSL 2 and Mac learners.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is an operating-system check insufficient for dispatch?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should a device fault preserve?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design an optional alternate GPU backend lesson.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **one container tag makes every NVIDIA device and driver equivalent.**

For the concrete failure exercise, why is an operating-system check insufficient for dispatch?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-062_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-062: Portability, operations and the cost of a GPU dependency.
Read courses/cuda/cpp/guides/cuda-062.md and courses/cuda/cpp/lessons/cuda-062.md.
Direct prerequisites: `cuda-003`, `cuda-008`, `cuda-030`, `cuda-061`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-062_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-062_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
