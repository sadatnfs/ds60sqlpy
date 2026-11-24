# cuda-061: From one pad to a maintainable CUDA project

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-010`, `cuda-011`, `cuda-024`, `cuda-025`

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Build a CMake CUDA project cleanly from source and pass its runtime tests on a declared target architecture.

Work through *From one pad to a maintainable CUDA project* with the concrete cases below. Finish with this evidence:
a clean reproducible build and actual runtime tests on a declared target. Distinguish an algorithmic
calculation, a compiled artifact and an actual device observation when explaining
what your work establishes.

## Purpose, vocabulary and mental model

A maintainable CUDA project separates interfaces, host orchestration and device implementation without hiding ownership. Host .cpp files compile as ordinary C++; .cu files contain CUDA compilation units; headers declare shared interfaces. Calls across device translation units can require separable compilation and device linking. CMake targets should state languages, dependencies and architecture policy explicitly. A project directory cannot be pasted into a single-source coding pad. Keep external project commands in an owned scratch directory with clear source and build paths, and validate both a clean build and actual execution on supported hardware.

### Key terms

- **CMake target:** A named library or executable with its own sources, properties and dependencies.
- **CUDA_ARCHITECTURES:** A CMake property that lists the GPU architectures to generate device code for.
- **Separable compilation:** Compiling device code in separate translation units so kernels can call device functions defined elsewhere.
- **Device linking:** A link step that resolves device symbols across separately compiled objects.

## How to run and study this lesson

Use the saved reading worksheet in `/classroom`; the reading pad does not execute
CUDA. For the bounded calculation, select **CPU model (Python)**, whose
answer-free starter supplies the literal fixtures and task contract. The
[CUDA C++ study workflow](../README.md) covers platforms, optional GPU
compilation and evidence labels. In a prepared Python environment you can also
run the separate [CPU reference](../references/cuda-061_cpu.py) from the
repository root:

```sh
python courses/cuda/cpp/references/cuda-061_cpu.py
```

Its assertions check the stated numerical result or model invariant; console
text is evidence of this CPU model only, not of CUDA execution.

## Worked example 1: trace the mechanism

A three-file design has include/transform.hpp declaring a host launch function, src/transform.cu defining its kernel and launch wrapper, and src/main.cpp building fixtures and validating output. The caller sees an ordinary host interface, while the implementation owns its CUDA dependencies.

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
project = {
    "include/transform.hpp": "host interface",
    "src/transform.cu": "kernel and launcher",
    "src/main.cpp": "fixture and validation",
    "build/": "generated artifacts",
}
assert len(project) == 4
print(project)
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{'include/transform.hpp': 'host interface', 'src/transform.cu': 'kernel and launcher', 'src/main.cpp': 'fixture and validation', 'build/': 'generated artifacts'}
```

Integers, shapes and ordering must match exactly; only assertions with an explicit
tolerance accept small floating-point differences. A printed duration is a model
output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

An undefined host launch function usually means its object was not linked or its declaration/definition disagree. An unresolved device function in another .cu file concerns device compilation/linking. These failures occur before mathematical validation and require different build fixes.

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

Name source and build directories in a clean out-of-source project.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why should architecture targets not come from lesson metadata argv?

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does a successful CMake configure prove?

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a project test split.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **a Makefile or CMake project can simply be pasted into the existing single-source pad.**

For the concrete failure exercise, why should architecture targets not come from lesson metadata argv?
Preserve the original input and the stage where behavior diverged, and compare
with the CPU model before changing hardware configuration.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/cuda-061_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

Check the documentation that matches your prepared toolkit before optional
hardware execution.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-061: From one pad to a maintainable CUDA project.
Read courses/cuda/cpp/guides/cuda-061.md and courses/cuda/cpp/lessons/cuda-061.md.
Direct prerequisites: `cuda-010`, `cuda-011`, `cuda-024`, `cuda-025`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-061_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-061_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
