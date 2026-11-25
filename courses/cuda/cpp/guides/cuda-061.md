# cuda-061: From one pad to a maintainable CUDA project

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-010`, `cuda-011`, `cuda-024`, `cuda-025`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Build a CMake CUDA project cleanly from source and pass its runtime tests on a declared target architecture.

**Scope:** `.cu` versus host `.cpp` translation units, headers, separable compilation, device linking, CMake targets, architecture lists, dependencies, tests and installable artifacts.

**Evidence to produce:** A clean reproducible build and actual runtime tests on a declared target.

## Purpose, vocabulary and mental model

A maintainable CUDA project separates interfaces, host orchestration and device implementation without hiding ownership. Host .cpp files compile as ordinary C++; .cu files contain CUDA compilation units; headers declare shared interfaces. Calls across device translation units can require separable compilation and device linking. CMake targets should state languages, dependencies and architecture policy explicitly. A project directory cannot be pasted into a single-source coding pad. Keep external project commands in an owned scratch directory with clear source and build paths, and validate both a clean build and actual execution on supported hardware.

### Key terms

- **CMake target:** A named library or executable with its own sources, properties and dependencies.
- **CUDA_ARCHITECTURES:** A CMake property that lists the GPU architectures to generate device code for.
- **Separable compilation:** Compiling device code in separate translation units so kernels can call device functions defined elsewhere.
- **Device linking:** A link step that resolves device symbols across separately compiled objects.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-061_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-061_cpu.py
```

## Worked example 1: trace the mechanism

A three-file design has include/transform.hpp declaring a host launch function, src/transform.cu defining its kernel and launch wrapper, and src/main.cpp building fixtures and validating output. The caller sees an ordinary host interface, while the implementation owns its CUDA dependencies.

**Why:** main.cpp sees only an ordinary host function, so it compiles with a host compiler and never touches kernel syntax.

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

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'include/transform.hpp': 'host interface', 'src/transform.cu': 'kernel and launcher', 'src/main.cpp': 'fixture and validation', 'build/': 'generated artifacts'}
```

**Check:** The reference asserts the four-entry project layout; also build and confirm main.cpp compiles as plain C++.

## Worked example 2: change a meaningful condition

An undefined host launch function usually means its object was not linked or its declaration/definition disagree. An unresolved device function in another .cu file concerns device compilation/linking. These failures occur before mathematical validation and require different build fixes.

**Why:** An undefined host symbol is a link problem, separate from device-code linking errors.

**Check:** Run the linker with verbose output and confirm the symbol resolves.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Declare the host launch function in include/transform.hpp, define kernel and launcher in src/transform.cu, and validate fixtures in src/main.cpp.

**Trap to avoid:** Putting the kernel declaration with triple-angle launch syntax in the header forces every includer to be compiled by nvcc.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Check that the object defining the launcher is linked and that declaration and definition signatures match.

**Trap to avoid:** Rewriting kernel math to fix a link error changes code that was never the cause.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Name source and build directories in a clean out-of-source project.

**Trap to avoid:** Building in the source tree mixes artifacts with maintained files.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why should architecture targets not come from lesson metadata argv?

**Trap to avoid:** Accepting flags from learner-controlled manifests lets arbitrary commands into builds.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does a successful CMake configure prove?

**Trap to avoid:** Calling the project working after configure skips compile errors.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a project test split.

**Trap to avoid:** Combining them means a missing GPU fails every test.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A Makefile or CMake project can simply be pasted into the existing single-source pad.** The pad compiles one source file through a fixed command, so it cannot run a build system. A real project lives in its own repository with an out-of-source build directory, explicit targets and an architecture policy. Worked example 1 sketches the three-file layout to create there, not inside the pad. Split tests into fast CPU reference checks and optional GPU checks that run only where a device exists.

## Self-check, retrieval and transfer

1. What are typical source and build directories for a clean project?
2. Why should architecture targets not come from lesson metadata argv?
3. What does a successful CMake configure prove?

Short answers are in the [separate explanations](../solutions/cuda-061_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
