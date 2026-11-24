# cuda-076: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Choose a sum identity

Use zero.

**Approach.** Pad inactive lanes of a sum reduction with 0, the additive identity. The reference stores `[2, 4, 6, 0]` in a four-lane tile and the block sum is 12.

**Why it is correct here.** Adding zero does not change a sum, so the padded lane contributes nothing while still occupying its slot in the tree. Every lane can therefore follow the same reduction steps without branching on validity.

**A plausible wrong approach.** Padding with the value of the last valid element, 6, changes the sum to 18. Such a pad looks harmless because it is in the data range, which is why it passes casual inspection.

**How to verify.** Evaluate `sum([2, 4, 6, 0])` and confirm it equals `sum([2, 4, 6]) = 12`. Repeat with a two-element tile padded with two zeros to show the identity holds for any pad count.

## Exercise 2: Choose a minimum identity

Use a sentinel outside the valid domain or carry validity.

**Approach.** For a minimum reduction pad with a value that can never win, such as positive infinity for floats or the dtype maximum for integers, or carry a separate validity flag with each value.

**Why it is correct here.** The pad must be the identity of `min`. If valid data can legally contain the dtype maximum, that sentinel ties with real data, so an explicit validity flag is safer when the whole domain is possible.

**A plausible wrong approach.** Padding with 0 is the common mistake carried over from sums. For data `[2, 4, 6]` it reports a minimum of 0, a value not in the input.

**How to verify.** Compute `min([2, 4, 6, inf])` and confirm 2. Then try an input made entirely of the sentinel value and check that the validity-flag version reports no valid minimum rather than the sentinel.

## Exercise 3: Trace barrier participants

All block lanes reach the barrier.

**Approach.** List every lane of the block, `[0, 1, 2, 3]`, and mark each one as reaching the barrier, including lane 3, which has no input element.

**Why it is correct here.** `cuda.syncthreads()` requires every thread in the block to arrive. The reference asserts `participants == [0,1,2,3]`, which models the rule that an inactive lane still participates in the collective operation.

**A plausible wrong approach.** Listing only lanes 0 to 2 because they hold data treats the barrier as a data operation. On hardware, a barrier not reached by all threads is undefined behavior and can hang or corrupt shared memory.

**How to verify.** Check that the participant list equals `range(blockDim)` regardless of the input length. A trace for a two-element input with a four-lane block should still show four participants.

## Exercise 4: Repair early return

Guard data access instead of participation.

**Approach.** Replace `if i >= n: return` with a guarded load: `value = x[i] if i < n else 0`, store `value` in shared memory, then let every thread proceed to the barrier and the reduction.

**Why it is correct here.** The guard now protects the memory access, not the control flow. The thread for index 3 never reads `x[3]`, yet it reaches every `syncthreads` call and contributes the identity value.

**A plausible wrong approach.** Moving the early return below the first barrier but above the second still leaves later barriers missing a participant. Every barrier after the return is affected, not only the first.

**How to verify.** Read the kernel and confirm no `return` appears before the last barrier. Run the CPU model with a three-element input and four lanes: the sum must be 12 and all four lanes recorded.

## Exercise 5: Separate block and grid scope

Shared memory is per block.

**Approach.** State that a shared-memory array belongs to one block. A result needing data from several blocks requires a second step, such as writing per-block partials to global memory and reducing them in another launch or with atomics.

**Why it is correct here.** Each block gets its own copy of the shared array, and `syncthreads` synchronizes only that block. Block 0 cannot see block 1's tile or wait for block 1 to finish.

**A plausible wrong approach.** Reading another block's partial from shared memory assumes a grid-wide shared space. The read returns the current block's own data, so the total silently counts one block several times.

**How to verify.** Use a two-block input and show the reduction produces two partials. The final answer equals the sum of the partials only after a separate combination step.

## Exercise 6: Design a nonmultiple test

Use n=blocksize+1 with explicit expected output.

**Approach.** Test with `n = blocksize + 1`, for example 5 elements and 4-lane blocks, using values whose sum is easy to compute by hand, like `[1, 2, 3, 4, 5]` with expected total 15.

**Why it is correct here.** This input needs two blocks, one of them almost empty. It exercises the padded lanes, the barrier participation of three inactive lanes, and the combination of two block partials.

**A plausible wrong approach.** Testing only with `n = 4` or `n = 8` makes every block full. Bugs in padding or early returns never execute, so the test passes against broken code.

**How to verify.** Write the expected partials explicitly, `[10, 5]`, and the total 15 before running. A mismatch in the second partial points directly to tail handling.

## Reference observation

All four modeled lanes participate; padded sum is 12.

The reference file is `courses/cuda/python/references/cuda-076_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
