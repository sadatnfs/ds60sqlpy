# cuda-056: Asynchronous copies, barriers and software pipelines

## Level and prerequisites

Advanced; about 130 minutes, plus any optional hardware experiment. Direct prerequisites: `cuda-019`, `cuda-028`, `cuda-036`, `cuda-039`

Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

Implement a two-stage asynchronous copy pipeline with correct tails and explain whether the overlap helped.

**Scope:** Producer/consumer stages, completion tokens, shared-memory lifetime, double buffering and alignment.

**Evidence to produce:** Correct tails, synchronization checks and a measured explanation of whether overlap helped.

## Purpose, vocabulary and mental model

Within-GPU asynchronous copy mechanisms can move tiles from global to shared storage while other work proceeds, subject to architecture, alignment and API requirements. These are different from host-to-device asynchronous transfers. A producer commits a stage, a consumer waits for its completion, and the stage cannot be overwritten until consumption finishes. Double buffering alternates two storage slots but does not remove these dependencies. Hardware-accelerated paths and fallback behavior must be checked for the exact toolchain and device. Correct tail loading and barrier participation remain essential even when the happy path overlaps efficiently.

### Key terms

- **memcpy_async:** A cooperative copy from global to shared memory that can proceed while threads do other work.
- **cuda::pipeline:** A libcu++ object that tracks stages of asynchronous copies through acquire, commit, wait and release.
- **Asynchronous barrier:** A `cuda::barrier` that separates arriving from waiting so threads can work between the two.
- **Software pipelining:** Overlapping the load of the next tile with computation on the current tile using several buffers.

## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/cuda-056_cpu.py) from the repository root:

```sh
python courses/cuda/cpp/references/cuda-056_cpu.py
```

## Worked example 1: trace the mechanism

For three tiles using two slots, tile 0 loads slot A and tile 1 loads slot B. Tile 2 may reuse A only after computation using tile 0 finishes. Copy completion permits reading; consumer completion permits reuse. Those are two different milestones.

**Why:** Copy completion allows reading, while consumer completion allows overwriting.

```python
states = ["free", "copying", "ready", "consuming", "done", "free"]
assert states.index("ready") < states.index("consuming") < states.index("done")
assert 16 % 16 == 0 and (16 + 4) % 16 != 0
print({"slot_lifetime": states, "offset_address_aligned_to_16": False})
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{'slot_lifetime': ['free', 'copying', 'ready', 'consuming', 'done', 'free'], 'offset_address_aligned_to_16': False}
```

**Check:** The reference asserts ready precedes consuming, which precedes done.

## Worked example 2: change a meaningful condition

A 16-byte transfer requirement does not mean an arbitrary pointer cast creates 16-byte alignment. An address offset by four bytes from an aligned base is still misaligned for that contract. Use valid alignment/layout or a supported fallback, and test the final partial tile separately.

**Why:** An address 4 bytes past an aligned base is not a multiple of 16.

**Check:** The reference asserts (16 + 4) % 16 != 0 and prints aligned False.

## Six progressive exercises

### Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Load tiles 0 and 1 into slots A and B, and reuse A for tile 2 only after tile 0's compute finishes.

**Trap to avoid:** Reusing A when tile 0's copy completed overwrites data still being computed on.

**Hint:** Start with the literal input and intermediate quantities in worked example 1.

### Exercise 2

Rework worked example 2 without copying its conclusion. Check the real address alignment before using a 16-byte transfer.

**Trap to avoid:** Casting the pointer to a 16-byte type does not change its address.

**Hint:** Identify exactly which condition changes in worked example 2.

### Exercise 3

List the lifetime states of one tile slot.

**Trap to avoid:** Collapsing ready and done into one state allows reuse too early.

**Hint:** Use the first worked example to establish the relevant quantities, then change only the requested input.

### Exercise 4

A consumer reads immediately after initiating a copy. Diagnose it.

**Trap to avoid:** Reading immediately sees stale or partial data.

**Hint:** Locate the failed phase or violated dependency before proposing a repair.

### Exercise 5

What happens to a partial final tile?

**Trap to avoid:** Filling the tile by over-reading past the end can fault.

**Hint:** Check what the algorithm is allowed to read, write or assume at this boundary.

### Exercise 6

Choose whether to add asynchronous staging.

**Trap to avoid:** Adding them because they sound faster can slow small kernels.

**Hint:** State the output contract and which observations are needed in the new application.

## Common mistakes and diagnosis

A tempting but incorrect claim: **Initiating a copy makes its destination immediately readable.** Issuing an asynchronous copy only starts the transfer, so the consumer must wait on its completion token or barrier before reading the destination. A second milestone governs reuse: a slot may be refilled only after the consumer has finished with it. Worked example 1 separates the two milestones for three tiles in two slots, and worked example 2 shows that alignment must be real, not cast into existence. Double buffering adds overlap but not correctness: with two slots, every refill still waits for the consumer of the tile that last used that slot.

## Self-check, retrieval and transfer

1. List the lifetime states of one tile slot.
2. When may tile 2 reuse slot A in worked example 1?
3. Is an address four bytes past a 16-byte aligned base valid for a 16-byte contract?
4. How should a partial final tile be handled?

Short answers are in the [separate explanations](../solutions/cuda-056_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

- [Asynchronous copies](https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/async-copies.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for cuda-056: Asynchronous copies, barriers and software pipelines.
Read courses/cuda/cpp/guides/cuda-056.md and courses/cuda/cpp/lessons/cuda-056.md.
Direct prerequisites: `cuda-019`, `cuda-028`, `cuda-036`, `cuda-039`
Review my own explanation and worksheet; give one progressive hint at a time.
Keep courses/cuda/cpp/solutions/cuda-056_solutions.md and GPU references closed until I request comparison.
Treat courses/cuda/cpp/references/cuda-056_cpu.py as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
