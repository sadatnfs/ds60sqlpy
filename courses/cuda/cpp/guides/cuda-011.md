# cuda-011: The `.cu` file, compiler driver and executable

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-003`, `cuda-009`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Work through *The `.cu` file, compiler driver and executable* with the concrete cases below. Finish with this evidence:
preserved compiler output plus a source-to-executable diagram. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A .cu translation unit can contain ordinary host functions and CUDA device functions. nvcc coordinates separate compilation paths, invokes a supported host compiler and links the CUDA runtime. PTX is a virtual instruction representation; a cubin holds device machine code for a target architecture. An executable can package several device images in a fat binary. Loading may select a compatible image or invoke supported JIT compilation of PTX. This explains why source compilation, host linking, device loading and kernel execution can fail at different times. Header suffix .cuh is a convention, not an instruction that executes anything.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-011_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-011_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

The manual lab command is `nvcc -std=c++17 -O2 -lineinfo main.cu -o main`. The input is main.cu; `-o main` names the executable. `./main` runs that file from the current directory. The toolkit's default target must support the actual device. A release build later needs deliberately selected architecture targets, not guessed values from a tutorial.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
stages = ["source", "host/device compilation", "link", "load", "execute", "validate"]
assert stages.index("link") < stages.index("execute")
assert stages.index("execute") < stages.index("validate")
print(" -> ".join(stages))
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
source -> host/device compilation -> link -> load -> execute -> validate
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

A missing semicolon is a source diagnostic. An undefined host function is a host-link diagnostic. 'No kernel image is available for execution on the device' is a loading/target problem. Replacing arithmetic in the kernel is unlikely to solve the latter. Save the complete diagnostic and identify the stage before changing versions.

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

Distinguish a .cu source file, PTX file and host executable.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is successful nvcc compilation not a GPU test?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does an executable permission error say about the kernel?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a release record for a compiled CUDA binary.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **an executable containing device code proves the device can execute it. .**

For the concrete failure exercise, why is successful nvcc compilation not a GPU test?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-011_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [Compiler workflow](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/nvcc.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-011: The `.cu` file, compiler driver and executable.
Read courses/cuda/cpp/guides/cuda-011.md and courses/cuda/cpp/lessons/cuda-011.md.
Direct prerequisites: `cuda-003`, `cuda-009`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-011_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-011_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
