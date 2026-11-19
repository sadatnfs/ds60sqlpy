# cuda-003: The software stack from application to driver

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-002`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *The software stack from application to driver* with the concrete cases below. Finish with this evidence:
correctly place six failure messages at their responsible layer. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

An application calls a runtime API or a higher-level library. User-space CUDA libraries then cooperate with the host NVIDIA driver to access a device. A container packages application code and user-space dependencies; it does not package a physical GPU or replace the host kernel driver. The toolkit includes tools such as the nvcc compiler. A framework wheel may bring compatible CUDA user-space components without a general-purpose CUDA compiler. Conversely, nvcc can exist on a machine where no GPU is visible. Each observation answers a different question: compilation, driver management access, framework device discovery, allocation and numerical execution are separate checks.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-003_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-003_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A shell reports `nvcc: command not found`, while an already installed framework executes a tensor operation on a GPU. This is possible because the framework can run precompiled kernels without the developer compiler. Building a new CUDA extension has a different dependency contract from running the existing tensor operator.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
checks = {"compiler": True, "device_visible": False, "kernel_validated": False}
assert checks["compiler"] and not checks["kernel_validated"]
print("Compilation evidence only; no GPU execution evidence.")
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
Compilation evidence only; no GPU execution evidence.
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A container contains nvcc and compiles a program, but `cudaGetDeviceCount` reports no available device. Editing the kernel cannot repair absent hardware access. Inspect host support, driver and deliberate container GPU exposure. The compiler result remains valid compilation evidence; record execution as unavailable instead of silently presenting a CPU result as CUDA success.

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

Order these layers: kernel driver, application, CUDA runtime, GPU.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A driver-management command succeeds but an allocation fails. What next?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What can a CPU-only Mac complete in this chapter?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a capability label for a build-only machine.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **installing a CUDA Python package or compiler installs a usable NVIDIA GPU.**

For the concrete failure exercise, a driver-management command succeeds but an allocation fails. What next?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-003_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-003: The software stack from application to driver.
Read courses/cuda/cpp/guides/cuda-003.md and courses/cuda/cpp/lessons/cuda-003.md.
Direct prerequisites: `cuda-002`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-003_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-003_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
