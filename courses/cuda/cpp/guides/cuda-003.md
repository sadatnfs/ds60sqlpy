# cuda-003: The software stack from application to driver

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-002`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Place six CUDA failure messages at the responsible layer of the stack, from application to host driver.

**Scope:** Host driver, CUDA runtime and driver APIs, toolkit, compiler, user-space libraries, framework packages and container image.

**Evidence to produce:** Correctly place six failure messages at their responsible layer.

## Purpose, vocabulary and mental model

An application calls a runtime API or a higher-level library. User-space CUDA libraries then cooperate with the host NVIDIA driver to access a device. A container packages application code and user-space dependencies; it does not package a physical GPU or replace the host kernel driver. The toolkit includes tools such as the nvcc compiler. A framework wheel may bring compatible CUDA user-space components without a general-purpose CUDA compiler. Conversely, nvcc can exist on a machine where no GPU is visible. Each observation answers a different question: compilation, driver management access, framework device discovery, allocation and numerical execution are separate checks.

### Key terms

- **CUDA runtime API:** The library interface, such as `cudaMalloc` and kernel launch syntax, that applications call to manage devices and work.
- **Host driver:** The NVIDIA driver installed on the host operating system that controls the physical GPU; a container image cannot supply it.
- **CUDA toolkit:** The developer package with `nvcc`, headers, libraries and tools for building CUDA programs.
- **nvidia-smi:** A driver management utility that reports visible GPUs and driver state but does not prove that a kernel computes correctly.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-003_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-003_cpu.py
```

## Worked example 1: trace the mechanism

A shell reports `nvcc: command not found`, while an already installed framework executes a tensor operation on a GPU. This is possible because the framework can run precompiled kernels without the developer compiler. Building a new CUDA extension has a different dependency contract from running the existing tensor operator.

**Why:** Framework wheels ship compiled device code and runtime libraries, so a tensor operation can execute on a machine with no compiler installed.

```python
checks = {"compiler": True, "device_visible": False, "kernel_validated": False}
assert checks["compiler"] and not checks["kernel_validated"]
print("Compilation evidence only; no GPU execution evidence.")
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
Compilation evidence only; no GPU execution evidence.
```

**Check:** Run the existing tensor operation and record its device, then separately attempt an extension build and record the missing compiler.

## Worked example 2: change a meaningful condition

A container contains nvcc and compiles a program, but `cudaGetDeviceCount` reports no available device. Editing the kernel cannot repair absent hardware access. Inspect host support, driver and deliberate container GPU exposure. The compiler result remains valid compilation evidence; record execution as unavailable instead of silently presenting a CPU result as CUDA success.

**Why:** cudaGetDeviceCount returning no devices depends on host driver and container exposure, which no change to kernel code can alter.

**Check:** Check host driver presence and the container's GPU exposure flags; device count must become nonzero before execution evidence exists.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Separate two capabilities: running prebuilt framework kernels, which needs a driver and runtime libraries, and compiling new kernels, which needs nvcc.

**Trap to avoid:** Concluding the GPU is broken because nvcc is missing confuses the compile dependency with the execute dependency.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Record the successful compilation as build evidence, then diagnose device visibility from the zero device count before touching any source.

**Trap to avoid:** Rewriting the kernel or adding a CPU fallback that prints success hides the missing hardware and produces a false GPU claim.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Order these layers: kernel driver, application, CUDA runtime, GPU.

**Trap to avoid:** Placing the runtime below the driver suggests the runtime can reach hardware directly, which would make driver diagnostics pointless.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A driver-management command succeeds but an allocation fails. What next?

**Trap to avoid:** Retrying the allocation in a loop without reading its status discards the error and can mask an out-of-memory condition.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What can a CPU-only Mac complete in this chapter?

**Trap to avoid:** Assuming Docker on the Mac passes a GPU through treats container packaging as hardware access, which it never provides.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a capability label for a build-only machine.

**Trap to avoid:** Labeling the machine CUDA-ready merges two claims and lets a reader assume kernels have produced validated results there.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Installing a CUDA Python package or compiler installs a usable NVIDIA GPU.** Packages and compilers are user-space software. Worked example 2 compiles successfully with nvcc yet `cudaGetDeviceCount` finds no device, because hardware access depends on a physical GPU, the host driver and deliberate container exposure. Installing software can never create the device itself.

## Self-check, retrieval and transfer

1. Which layer must exist on the host and cannot be supplied by a container image?
2. Why can a framework run GPU tensors on a machine where `nvcc` is missing?
3. What label would you give a successful nvcc build on a machine with no GPU?

Short answers are in the [separate explanations](../solutions/cuda-003_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
