# cuda-016: explanatory solutions

## Mechanism review

Storage spaces describe accessibility and lifetime as well as likely performance. Global allocations can hold data used by many kernels. Shared memory belongs to a block and lasts for that block's execution. Registers hold thread-local values, but a large local array or register pressure can place values in local memory backed by device memory. Constant storage is useful for certain read-only patterns, especially broadcast-like access, but it is not an automatic speedup for arbitrary divergent addresses. A compiler resource report helps explain implementation choices; source variable scope alone does not prove where every value resides.

## Exercise 1

In a three-tap filter, the input and output images live in global allocations. A thread's running sum is a scalar candidate for a register. A cooperatively loaded tile belongs in shared memory. Three common coefficients may use read-only or constant storage. These are choices to validate, not declarations that force a faster program.

**Approach:** Map each object to a space: images in global, sum in a register, tile in shared, taps in constant.

**Why it is correct:** Each choice follows the scope and reuse of the data, not a speed promise.

**A plausible wrong approach:** Declaring every value __shared__ wastes shared capacity on per-thread sums and limits resident blocks.

**How to verify:** Inspect compiler resource output and confirm the tile size matches the shared bytes reported.

## Exercise 2

A per-thread temporary array with 1,024 floats needs 4,096 bytes per thread. At 128 threads that is 524,288 bytes of logical temporary data, before other resources. Calling it 'local' does not make it inexpensive. Reduce live working state or choose a different algorithm, then inspect compiler and runtime evidence.

**Approach:** Multiply 1,024 floats by 4 bytes, then by 128 threads.

**Why it is correct:** 4,096 bytes per thread far exceeds register capacity, so it lives in device-backed local memory.

**A plausible wrong approach:** Assuming 'local' means on-chip predicts fast access for 524,288 bytes that actually travel to DRAM.

**How to verify:** The reference asserts 4096 and 524288; compare with spill or stack size in compiler output.

## Exercise 3

Global allocation for the image, shared memory for cooperating block data, and a local scalar that the compiler may keep in a register.

**Approach:** Match each object's scope: grid-wide image, block-wide tile, per-thread scalar.

**Why it is correct:** Global memory outlives blocks, shared memory lives per block, and a scalar suits registers.

**A plausible wrong approach:** Putting the image tile in global memory and reloading it per thread forgoes the reuse that motivated tiling.

**How to verify:** Check that the reference's storage_roles dictionary matches your three assignments.

## Exercise 4

The compiler can place local data in device-backed local memory or spill registers. Inspect generated resource information and measured behavior.

**Approach:** Replace 'guaranteed' with 'may be kept in registers' and cite the compiler's spill report.

**Why it is correct:** Register allocation is a compiler decision constrained by the per-thread register limit.

**A plausible wrong approach:** Adding register keywords to force placement has no effect on modern CUDA compilers.

**How to verify:** Compile with resource usage reporting and look for local memory or spill bytes.

## Exercise 5

No. Ordinary block shared memory has block scope. Specialized cluster mechanisms have separate feature and synchronization contracts.

**Approach:** State that ordinary shared memory is visible only within one block.

**Why it is correct:** Each block gets its own shared allocation, which ends when that block exits.

**A plausible wrong approach:** Passing a shared array address to another block and reading it yields undefined results.

**How to verify:** Write one value per block to global memory instead and read it in a later kernel.

## Exercise 6

Compare whether neighboring lanes read the same entries or divergent entries, access frequency and update needs; measure against a suitable read-only/global alternative.

**Approach:** Compare access pattern: constant cache broadcasts when a warp reads one address, serializes otherwise.

**Why it is correct:** A 64-entry table fits easily, so the deciding factor is whether lanes read the same entry.

**A plausible wrong approach:** Choosing constant storage for data-dependent lookups serializes divergent reads in the warp.

**How to verify:** Measure both variants on inputs with uniform and divergent indices.

## Self-check answers

1. **Which storage would you choose for three filter coefficients that every thread reads?** Constant or read-only storage, because all threads read the same few values.
2. **When does shared memory's content disappear?** When the block that owns it finishes executing.
3. **Why can a per-thread array of 1,024 floats hurt occupancy?** It needs 4 KB per thread, which spills to local memory and inflates per-thread resources.

## Numerical reference and its limits

The [CPU reference](../references/cuda-016_cpu.py) reproduces worked example 1 and prints `{'logical_temporary_bytes': 524288, 'storage_roles': {'image': 'global', 'cooperative_tile': 'shared', 'sum': 'thread local'}}`.

## Transfer review

Compare whether neighboring lanes read the same entries or divergent entries, access frequency and update needs; measure against a suitable read-only/global alternative.
