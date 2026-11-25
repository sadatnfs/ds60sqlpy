# cuda-057: Clusters, TMA and newer GPU execution features

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-055`, `cuda-056`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a feature-gated cluster or TMA path with a fallback and explain its data visibility rules.

**Scope:** Thread-block clusters, distributed shared memory, tensor memory accelerator transfers, architecture-specific barriers and warpgroup work.

**Evidence to produce:** A feature-gated implementation with fallback and a correct explanation of data visibility.

## Purpose, vocabulary and mental model

Thread-block clusters and tensor memory accelerator mechanisms expand cooperation and data movement on supported newer architectures. Distributed shared memory changes which participating blocks can access certain shared regions, but introduces cluster lifetime and synchronization requirements. TMA transfers use descriptors and completion protocols; they are not ordinary memcpy calls with a new name. Different instructions can require architecture-specific targets beyond a broad compute-capability family. Maintain a feature table for the exact operation, compiler and GPU, and retain a portable fallback. Learning the ownership diagram is useful without executing architecture-specific code.

### Key terms

- **Thread block cluster:** A group of blocks scheduled together on nearby SMs, available on compute capability 9.0 and later.
- **Distributed shared memory:** Access by one block in a cluster to the shared memory of another block in the same cluster.
- **Tensor Memory Accelerator (TMA):** A hardware unit that copies multidimensional tiles described by a tensor map descriptor.
- **Feature gate:** A compile-time and runtime check that selects an advanced path only on supported devices and keeps a fallback.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-057_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-057_cpu.py
```

## Worked example 1: trace the mechanism

A cluster-assisted histogram can combine partial bins across cooperating blocks before global output. Before a remote shared-memory read, the producing block's storage must be initialized and remain alive through the required cluster synchronization. A block exiting early can invalidate the assumed lifetime.

**Why:** The cluster barrier guarantees the producer's bins are written and its shared storage still exists when a neighbor reads it.

```python
capabilities = {"baseline": True, "cluster_histogram": False, "TMA_qualified": False}
selected = "cluster_histogram" if capabilities["cluster_histogram"] else "baseline"
assert selected == "baseline"
print({"selected_implementation": selected, "specialized_execution_verified": False})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'selected_implementation': 'baseline', 'specialized_execution_verified': False}
```

**Check:** Compare merged bins against a host histogram of the same input, and run on supported hardware only; otherwise record the check as unavailable.

## Worked example 2: change a meaningful condition

A feature table might mark baseline kernels available, cluster launch unavailable and a TMA experiment unqualified. Dispatch should choose the baseline, not attempt an unsupported instruction and silently label a CPU calculation as the specialized result. Feature detection is per operation, not a marketing-name comparison.

**Why:** The baseline computes the same counts on any supported device, so choosing it keeps results correct.

**Check:** The reference asserts selected == 'baseline' and prints specialized_execution_verified False.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Each block writes partial histogram bins to its shared memory, the cluster synchronizes, then blocks read remote bins and merge them before one global write.

**Trap to avoid:** Reading a neighbor's distributed shared memory before the cluster sync, or after the producer block exits, reads uninitialized or freed storage.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Consult the capability table and dispatch to the baseline kernel when cluster launch and TMA are not qualified.

**Trap to avoid:** Trying the cluster instruction and catching a failure, then labeling a CPU result as the cluster path, misreports what ran.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

List fields for an architecture-specific capability record.

**Trap to avoid:** Recording only the GPU model name omits the compiler target and launch evidence that decide support.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

Why does a higher-looking GPU name not prove every instruction is supported?

**Trap to avoid:** Assuming a larger model number includes every earlier specialized instruction can produce code the device cannot load.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What should an unavailable cluster feature do to reading progress?

**Trap to avoid:** Blocking completion until a cluster-capable GPU appears punishes learners for hardware they cannot control.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Design a fallback histogram interface.

**Trap to avoid:** Letting the fallback use different bin boundaries makes outputs differ silently between devices.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **A later-looking architecture name automatically supports every architecture-specific instruction variant.** Instruction variants are tied to specific architectures, toolkit versions and compile targets, not to how new a product name sounds. Detect the feature with a real probe and record the result. Worked example 2 dispatches the baseline when cluster launch is unavailable instead of trying an unsupported instruction.

## Self-check, retrieval and transfer

1. Name four fields of a capability record.
2. What should an unavailable cluster feature do to reading progress?
3. When may a block read another block's distributed shared memory?

Short answers are in the [separate explanations](../solutions/cuda-057_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-057: Clusters, TMA and newer GPU execution features.
Read courses/cuda/cpp/guides/cuda-057.md and courses/cuda/cpp/lessons/cuda-057.md.
Direct prerequisites: `cuda-055`, `cuda-056`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-057_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-057_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
