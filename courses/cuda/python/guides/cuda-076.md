# cuda-076: Shared memory and collective responsibility

**Route:** CUDA Python and machine learning. **Stage:** intermediate. **Prerequisites:** `cuda-002`, `cuda-075`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- Choose a sum identity.
- Choose a minimum identity.
- Trace barrier participants.
- Repair early return.
- Separate block and grid scope.
- Design a nonmultiple test.

## Mechanism and vocabulary

Shared memory is a block-local cooperation area. Threads load assigned pieces, synchronize, then consume data another thread may have produced. A barrier is a collective obligation: all threads that participate in a block must reach compatible synchronization points. Returning early for a tail lane before a required barrier can leave other threads waiting or produce undefined behavior.

For a partial tile, valid lanes load input while invalid lanes write the operation's identity, such as zero for a sum. Every lane still reaches the barrier. The identity is algorithm-specific: minimum needs a suitably large sentinel, and a weighted average needs counts as well as sums. Shared storage does not communicate between arbitrary blocks; cross-block cooperation needs a separate algorithm or explicitly supported launch mechanism.



### Key terms

- **Shared memory:** Fast on-chip memory visible to all threads of one block and lasting only for that block's lifetime.
- **Block barrier:** A collective such as `cuda.syncthreads()` that every thread in the block must reach before any thread proceeds.
- **Identity element:** A value that leaves a reduction unchanged, such as zero for addition, used to fill inactive slots.
- **Early return before a barrier:** A thread leaving the kernel before a barrier, which leaves the collective incomplete and produces undefined behavior.

## Worked examples

### Worked example 1

A four-lane tile reads [2,4,6] and stores [2,4,6,0]. All four lanes synchronize, then the block computes sum 12.

### Worked example 2

Replacing the invalid lane with an early return is unsafe when later code has a block barrier. Keeping that lane active with a neutral value preserves collective participation.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-076_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-076_cpu.py
```

```python
tile = [2, 4, 6]
width = 4
shared = [tile[i] if i < len(tile) else 0 for i in range(width)]
participants = list(range(width))
assert participants == [0, 1, 2, 3]
assert sum(shared) == 12
print("CPU cooperative model:", shared, sum(shared))
```

**Expected observation:** All four modeled lanes participate; padded sum is 12.

**Variable trace.** Before running the model, predict these final values; then compare:

| Variable | Final value |
|---|---|
| `tile` | `[2, 4, 6]` |
| `width` | `4` |
| `shared` | `[2, 4, 6, 0]` |
| `participants` | `[0, 1, 2, 3]` |

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-076.md) before opening hints.

### Exercise 1: Choose a sum identity

**Trap to avoid:** Padding with the value of the last valid element, 6, changes the sum to 18. Such a pad looks harmless because it is in the data range, which is why it passes casual inspection.

### Exercise 2: Choose a minimum identity

**Trap to avoid:** Padding with 0 is the common mistake carried over from sums. For data `[2, 4, 6]` it reports a minimum of 0, a value not in the input.

### Exercise 3: Trace barrier participants

**Trap to avoid:** Listing only lanes 0 to 2 because they hold data treats the barrier as a data operation. On hardware, a barrier not reached by all threads is undefined behavior and can hang or corrupt shared memory.

### Exercise 4: Repair early return

**Trap to avoid:** Moving the early return below the first barrier but above the second still leaves later barriers missing a participant. Every barrier after the return is affected, not only the first.

### Exercise 5: Separate block and grid scope

**Trap to avoid:** Reading another block's partial from shared memory assumes a grid-wide shared space. The read returns the current block's own data, so the total silently counts one block several times.

### Exercise 6: Design a nonmultiple test

**Trap to avoid:** Testing only with `n = 4` or `n = 8` makes every block full. Bugs in padding or early returns never execute, so the test passes against broken code.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. Ask which value leaves a sum unchanged when it is added to a padded lane.
2. Zero can be a real minimum. Pick a value no real input can reach, or carry a separate valid flag.
3. Count the lanes in the block, not the input elements, and ask which must arrive at the barrier.
4. Move the length check from the top of the kernel to the load, so the lane stays active but reads nothing.
5. Ask whether one block's shared array is visible to a thread in a different block.
6. Pick a length one larger than the block size and write the expected padded result before running.

## Common mistakes and self-check

The dangerous mistake is letting a tail lane return early before a block barrier. Other lanes then wait at a synchronization point that not every thread reaches, which can hang or produce undefined behavior. Another mistake is padding with a value that is not the identity, such as zero for a minimum. Fix the first by guarding only the data access while every lane still reaches the barrier, and the second by choosing an algorithm-specific identity or a validity flag.

**Evidence limit:** The model lists four participating lanes and a padded sum of 12. It is a sequential trace, so it cannot detect a missing barrier, a shared-memory race or a hang; those only appear when a real block runs on a device.

1. What makes a barrier a collective obligation?
2. Why is the identity value algorithm-specific?
3. Can shared memory pass data between two blocks?

Answers: [self-check answers](../solutions/cuda-076_solutions.md#self-check-answers).

## Primary references

- [NVIDIA CUDA Python introduction](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-076: Shared memory and collective responsibility.
Read courses/cuda/python/guides/cuda-076.md and courses/cuda/python/lessons/cuda-076.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
