# cuda-062: Portability, operations and the cost of a GPU dependency

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-003`, `cuda-008`, `cuda-030`, `cuda-061`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Write a deployment checklist tied to evidence tiers that fails gracefully when no supported GPU is present.

**Scope:** Feature detection, compatible driver/toolkit/library combinations, binary targets, runtime fallbacks, architecture-specific code, memory budgets, warm-up, diagnostics and fault reporting.

**Evidence to produce:** A deployment checklist tied to supported evidence tiers and graceful failures.

## Purpose, vocabulary and mental model

Portability means defining what is supported and how unsupported situations behave. CUDA execution requires a supported NVIDIA device and host software path; a CPU-only classroom can still teach algorithms and validate CPU references. AMD, Intel and Apple GPU programming use different backends and APIs, not an automatic CUDA compatibility promise. Detect capability for the operation, not simply the operating-system name. Containers package user-space dependencies but share host driver and hardware constraints. MIG, MPS, device sharing and resets are operator-managed topics. A teaching worker must never silently reset a shared device or erase learner state to recover from a fault.

### Key terms

- **Capability detection:** Querying device count, compute capability and driver version before selecting a code path.
- **Graceful failure:** Stopping with a clear message and a nonzero exit instead of crashing or silently producing wrong output.
- **Driver compatibility:** Whether the installed driver supports the CUDA runtime version and device code that the binary contains.
- **Evidence tier:** A labeled level of proof, such as compiled, executed on a GPU or benchmarked, attached to a claim.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-062_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-062_cpu.py
```

## Worked example 1: trace the mechanism

A dispatch policy offers CPU reference on every ordinary classroom and CUDA execution only after visibility, allocation and a small numerical probe succeed. It records which path actually ran. The same expected mathematical result does not make CPU output evidence of CUDA execution.

**Why:** The probe checks that the device actually computes correctly, and logging the chosen path records what really ran.

```python
capability = {"reading": True, "CPU_reference": True, "CUDA_device_probe": False}
selected = "CUDA" if capability["CUDA_device_probe"] else "CPU_reference"
assert selected == "CPU_reference"
print({"selected_path": selected, "CUDA_execution": "unavailable"})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'selected_path': 'CPU_reference', 'CUDA_execution': 'unavailable'}
```

**Check:** The reference asserts selected == 'CPU_reference' when the probe is False and prints CUDA_execution unavailable.

## Worked example 2: change a meaningful condition

A model fits on one 24 GiB GPU but fails on an 8 GiB device. The container tag is identical; the resource contract is not. Reduce the bounded workload or choose a supported alternate path, preserving the original memory error and learner source.

**Why:** A model fitting 24 GiB does not fit 8 GiB regardless of container tag.

**Check:** Run on the smaller device and confirm the original memory error is preserved and reported.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Offer the CPU reference everywhere, and enable CUDA only after device visibility, allocation and a small numerical probe all succeed.

**Trap to avoid:** Reporting the CUDA path because the expected numbers matched hides that the CPU reference produced them.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Check the model's memory need against device memory and shrink the workload or choose another path.

**Trap to avoid:** Assuming the same image guarantees the same resources hides the memory limit.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Write a supported-surface table for Linux, WSL 2 and Mac learners.

**Trap to avoid:** Promising Mac CUDA execution sets expectations the platform cannot meet.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why is an operating-system check insufficient for dispatch?

**Trap to avoid:** Dispatching on OS name alone selects CUDA on Linux machines without GPUs.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should a device fault preserve?

**Trap to avoid:** Resetting hardware or volumes destroys unrelated state.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design an optional alternate GPU backend lesson.

**Trap to avoid:** Presenting it as running CUDA kernels misleads learners.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **One container tag makes every NVIDIA device and driver equivalent.** A container fixes user space software, but the driver, device architecture and memory come from the host. Worked example 2 shows the same tag fitting a 24 GiB device and failing on an 8 GiB one. Dispatch on detected capability and a small numerical probe, and record which path actually ran. A smaller device may need a reduced workload, but report the reduction and keep the original memory error, so a fit on 8 GiB is not mistaken for the full model.

## Self-check, retrieval and transfer

1. Why is an operating-system check insufficient for dispatch?
2. What should a device fault preserve?
3. In worked example 1, when does the CUDA path run?

Short answers are in the [separate explanations](../solutions/cuda-062_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
