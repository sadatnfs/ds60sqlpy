# cuda-106: explained solutions

Compare with your [worksheet](../lessons/cuda-106.md) attempt.

## Exercise 1: Create tile boundaries

Use half-open intervals.

**Approach.** Create tile boundaries as half-open intervals `[start, min(start + tile, n))` with `start` stepping by 4 from 0: for `n = 10` this yields `[0..3]`, `[4..7]` and `[8, 9]`.

**Why it is correct here.** Half-open intervals tile the index range without overlap or gaps, because each tile ends exactly where the next begins. The `min` call caps the last tile at `n`.

**A plausible wrong approach.** Using closed intervals `[start, start + tile]` makes adjacent tiles share an element, so index 4 is processed twice and a sum reduction double counts it.

**How to verify.** The reference asserts the three tiles and that their flattened concatenation equals `list(range(10))`, which checks both coverage and the absence of duplicates.

## Exercise 2: Mask a final tile

Guard both input and output.

**Approach.** Mask the final tile: the third tile has lanes for offsets 8 through 11, of which only 8 and 9 are valid, so loads and stores both take a mask `offsets < n`.

**Why it is correct here.** A tile DSL operates on fixed-size tiles, so lanes beyond the array exist in the computation. Masking the load prevents reading past the buffer, and masking the store prevents writing past it.

**A plausible wrong approach.** Masking only the store still issues out-of-bounds loads, which can fault or read unrelated memory, and an unmasked reduction then includes garbage values.

**How to verify.** Run with `n = 10` and a tile of 4, fill a guard region after the output with a sentinel, and confirm the sentinel is untouched and outputs match the reference.

## Exercise 3: Compare thread and tile abstractions

The compiler owns more mapping decisions in a tile DSL.

**Approach.** Compare abstractions: in thread-level CUDA the programmer maps each thread to elements and manages shared memory, while in a tile DSL the programmer writes operations on whole tiles and the compiler decides thread mapping, vectorization and staging.

**Why it is correct here.** The tile model moves decisions such as which thread loads which element into the compiler. That reduces code for common patterns but limits control when the compiler's choice is poor.

**A plausible wrong approach.** Assuming a tile kernel behaves like a thread kernel with the same block size misreads the model, since a tile program instance is not a single thread.

**How to verify.** Write the same vector add in both styles and list which decisions appear explicitly in each source, such as index computation and bounds checks.

## Exercise 4: State compiler requirements

Record exact release and supported architecture.

**Approach.** State compiler requirements: record the exact DSL release, the backend compiler version it needs and the supported GPU architectures, since tile DSLs change quickly.

**Why it is correct here.** Tile DSLs often support only recent architectures and change their APIs between releases. Without recorded versions a kernel that compiled once may not compile later.

**A plausible wrong approach.** Writing that the kernel requires a recent version gives no way to reproduce the build.

**How to verify.** Put pinned versions in the lesson's requirements and check them at the start of the GPU run, failing with a clear message when they do not match.

## Exercise 5: Design a library comparison

Match data shape dtype and timing boundary.

**Approach.** Design a comparison against a library routine with the same data shape, dtype and timing boundary, such as both including or both excluding the first compile.

**Why it is correct here.** Tile DSL kernels usually compile on first call. If one side includes compilation and the other does not, the comparison measures setup rather than execution.

**A plausible wrong approach.** Timing the DSL kernel once against a warmed library call reports the DSL as much slower purely because of compilation.

**How to verify.** Report the first-call time and the steady-state median separately for both implementations, and check outputs agree before comparing times.

## Exercise 6: Explain a resource tradeoff

Larger tiles can increase live state and reduce concurrency.

**Approach.** Explain the resource tradeoff of larger tiles: they can increase reuse of loaded data but hold more values in registers or shared memory, which can reduce how many tile instances run concurrently.

**Why it is correct here.** Concurrency hides memory latency. If larger tiles reduce occupancy enough, the reuse gain can be outweighed, so the net effect depends on the device and shape.

**A plausible wrong approach.** Concluding that larger tiles are always faster because they reuse more data predicts a direction that only device evidence can establish.

**How to verify.** Measure several tile sizes on the target device and record register usage and achieved occupancy beside timings.

## Self-check answers

1. **What does a tile-level language change for the programmer?** The programmer describes operations on blocks of data, and the compiler chooses how to distribute them over threads and instructions.

2. **Why use half-open tile intervals?** Each tile ends where the next begins, so every element is covered exactly once without overlap.

3. **Does opening this lesson give the Python worker a DSL compiler?** No. It provides a CPU tiling model only; a DSL needs a prepared environment with a supported device.

## Reference observation

Three tiles cover ten elements exactly once.

Asserted by `courses/cuda/python/references/cuda-106_cpu.py`.
