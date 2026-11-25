# cuda-011: The `.cu` file, compiler driver and executable

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-003`, `cuda-009`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Compile one `main.cu` with a reviewed `nvcc` command and draw its source-to-executable artifact diagram.

**Scope:** Host and device compilation, `.cu`/`.cuh`, host compiler compatibility, runtime linking, PTX, cubin, fatbinary and just-in-time loading.

**Evidence to produce:** Preserved compiler output plus a source-to-executable diagram.

## Purpose, vocabulary and mental model

A .cu translation unit can contain ordinary host functions and CUDA device functions. nvcc coordinates separate compilation paths, invokes a supported host compiler and links the CUDA runtime. PTX is a virtual instruction representation; a cubin holds device machine code for a target architecture. An executable can package several device images in a fat binary. Loading may select a compatible image or invoke supported JIT compilation of PTX. This explains why source compilation, host linking, device loading and kernel execution can fail at different times. Header suffix .cuh is a convention, not an instruction that executes anything.

### Key terms

- **nvcc:** The CUDA compiler driver that separates host and device code, calls a host compiler and links the CUDA runtime.
- **PTX:** A virtual GPU instruction set that the driver can just-in-time compile for a compatible architecture.
- **cubin:** A binary that holds native device machine code for one specific GPU architecture.
- **Fat binary:** An embedded bundle of several device images, such as cubins for multiple architectures plus PTX.
- **JIT compilation:** Just-in-time translation of PTX into machine code when a module is loaded on a device.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-011_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-011_cpu.py
```

## Worked example 1: trace the mechanism

The manual lab command is `nvcc -std=c++17 -O2 -lineinfo main.cu -o main`. The input is main.cu; `-o main` names the executable. `./main` runs that file from the current directory. The toolkit's default target must support the actual device. A release build later needs deliberately selected architecture targets, not guessed values from a tutorial.

**Why:** Each flag maps to a stage; -lineinfo keeps source mapping for later profiling without debug slowdown.

```python
stages = ["source", "host/device compilation", "link", "load", "execute", "validate"]
assert stages.index("link") < stages.index("execute")
assert stages.index("execute") < stages.index("validate")
print(" -> ".join(stages))
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
source -> host/device compilation -> link -> load -> execute -> validate
```

**Check:** Run nvcc --version and the device query, then confirm the chosen target covers that compute capability.

## Worked example 2: change a meaningful condition

A missing semicolon is a source diagnostic. An undefined host function is a host-link diagnostic. 'No kernel image is available for execution on the device' is a loading/target problem. Replacing arithmetic in the kernel is unlikely to solve the latter. Save the complete diagnostic and identify the stage before changing versions.

**Why:** Each stage has different causes, so the stage determines whether to edit source, link inputs or targets.

**Check:** Save the full diagnostic text and confirm the fix targets the stage it names.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Read each part of the command: language standard, optimization, line info, input file and output name.

**Trap to avoid:** Copying an -arch value from a tutorial can build code for a different architecture than the installed device.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Classify each message by stage: compile, link or load, before changing anything.

**Trap to avoid:** Editing kernel arithmetic to fix 'no kernel image' changes code that never ran on the device.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Distinguish a .cu source file, PTX file and host executable.

**Trap to avoid:** Calling PTX machine code ignores that the driver may still translate it for the real device.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is successful nvcc compilation not a GPU test?

**Trap to avoid:** Reporting a GPU pass from a CI build job without a device claims execution that never occurred.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What does an executable permission error say about the kernel?

**Trap to avoid:** Rebuilding with a different -arch cannot fix a missing execute permission.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a release record for a compiled CUDA binary.

**Trap to avoid:** Recording only the toolkit version leaves the supported architectures unknown.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **An executable containing device code proves the device can execute it.** Packaging device code shows only what targets were compiled. Worked example 2 lists the loading error 'no kernel image is available', which occurs when the executable lacks a cubin or compatible PTX for the actual GPU. Execution evidence requires a run on the target device.

## Self-check, retrieval and transfer

1. What is the difference between PTX and a cubin?
2. Which diagnostic class is an undefined host function?
3. What should a release record include for a CUDA binary?

Short answers are in the [separate explanations](../solutions/cuda-011_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
