# cuda-016: GPU memory spaces in one working program

## Level and prerequisites

Beginner; about 90 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-013`, `cuda-015`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Justify a storage space for each kernel variable and verify the result on two input shapes.

**Scope:** Registers, local memory, global memory, shared memory, constant memory and caches; storage scope and lifetime versus hardware location.

**Evidence to produce:** A justified storage choice for each variable and a correct result across two input shapes.

## Purpose, vocabulary and mental model

Storage spaces describe accessibility and lifetime as well as likely performance. Global allocations can hold data used by many kernels. Shared memory belongs to a block and lasts for that block's execution. Registers hold thread-local values, but a large local array or register pressure can place values in local memory backed by device memory. Constant storage is useful for certain read-only patterns, especially broadcast-like access, but it is not an automatic speedup for arbitrary divergent addresses. A compiler resource report helps explain implementation choices; source variable scope alone does not prove where every value resides.

### Key terms

- **Register:** The fastest per-thread storage, allocated by the compiler from a finite per-SM register file.
- **Local memory:** Per-thread storage that the compiler places in device memory, for example for spills or large local arrays.
- **Shared memory:** On-chip storage visible to all threads of one block for the lifetime of that block.
- **Constant memory:** Read-only device storage with a dedicated cache that suits one value broadcast to many threads.
- **Global memory:** Device DRAM visible to every thread and kernel, with the largest capacity and the highest latency.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-016_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-016_cpu.py
```

## Worked example 1: trace the mechanism

In a three-tap filter, the input and output images live in global allocations. A thread's running sum is a scalar candidate for a register. A cooperatively loaded tile belongs in shared memory. Three common coefficients may use read-only or constant storage. These are choices to validate, not declarations that force a faster program.

**Why:** Each choice follows the scope and reuse of the data, not a speed promise.

```python
bytes_per_thread = 1024 * 4
logical_bytes_per_block = bytes_per_thread * 128
assert bytes_per_thread == 4096 and logical_bytes_per_block == 524288
placements = {"image": "global", "cooperative_tile": "shared", "sum": "thread local"}
print({"logical_temporary_bytes": logical_bytes_per_block, "storage_roles": placements})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'logical_temporary_bytes': 524288, 'storage_roles': {'image': 'global', 'cooperative_tile': 'shared', 'sum': 'thread local'}}
```

**Check:** Inspect compiler resource output and confirm the tile size matches the shared bytes reported.

## Worked example 2: change a meaningful condition

A per-thread temporary array with 1,024 floats needs 4,096 bytes per thread. At 128 threads that is 524,288 bytes of logical temporary data, before other resources. Calling it 'local' does not make it inexpensive. Reduce live working state or choose a different algorithm, then inspect compiler and runtime evidence.

**Why:** 4,096 bytes per thread far exceeds register capacity, so it lives in device-backed local memory.

**Check:** The reference asserts 4096 and 524288; compare with spill or stack size in compiler output.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Map each object to a space: images in global, sum in a register, tile in shared, taps in constant.

**Trap to avoid:** Declaring every value __shared__ wastes shared capacity on per-thread sums and limits resident blocks.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Multiply 1,024 floats by 4 bytes, then by 128 threads.

**Trap to avoid:** Assuming 'local' means on-chip predicts fast access for 524,288 bytes that actually travel to DRAM.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

Assign storage for a reused image, a block tile and a scalar sum.

**Trap to avoid:** Putting the image tile in global memory and reloading it per thread forgoes the reuse that motivated tiling.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

An author says a local array is guaranteed to stay in registers. Correct the claim.

**Trap to avoid:** Adding register keywords to force placement has no effect on modern CUDA compilers.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

Can one block read another block's ordinary shared array?

**Trap to avoid:** Passing a shared array address to another block and reading it yields undefined results.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Decide whether to use constant storage for a 64-entry lookup table.

**Trap to avoid:** Choosing constant storage for data-dependent lookups serializes divergent reads in the warp.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Every local variable stays in a register, or shared memory is shared across all blocks.** The compiler decides where locals live: large or dynamically indexed arrays and register pressure push values into local memory, which is backed by device memory. Shared memory is private to one block for that block's lifetime, so another block can never read it. Worked example 2 shows how quickly 'local' data grows.

## Self-check, retrieval and transfer

1. Which storage would you choose for three filter coefficients that every thread reads?
2. When does shared memory's content disappear?
3. Why can a per-thread array of 1,024 floats hurt occupancy?

Short answers are in the [separate explanations](../solutions/cuda-016_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-016: GPU memory spaces in one working program.
Read courses/cuda/cpp/guides/cuda-016.md and courses/cuda/cpp/lessons/cuda-016.md.
Direct prerequisites: `cuda-013`, `cuda-015`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-016_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-016_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
