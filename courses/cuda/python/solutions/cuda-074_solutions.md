# cuda-074: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute launch size for n=17

Five blocks of four are enough.

**Approach.** Use ceiling division: `blocks = (n + block - 1) // block`, which for `n = 17` and `block = 4` gives `(17 + 3) // 4 = 5` blocks and 20 lanes.

**Why it is correct here.** Four blocks provide only 16 lanes and would skip index 16. Five blocks provide 20 lanes, which covers every index from 0 to 16 with three spare lanes in the last block.

**A plausible wrong approach.** Computing `n // block = 4` blocks is the floor-division mistake; the program runs without error and the last element is never written, so its output slot keeps whatever value was in the allocation.

**How to verify.** Evaluate the expression in Python and confirm it returns 5. Extend the reference model with `n = 17`: the list `visits` must equal `list(range(17))`, which holds only with five blocks and the `< n` guard.

## Exercise 2: Trace the last block

Indices 17..19 are out of range.

**Approach.** List the global indices of the last block for `n = 17`: block 4 covers `4*4 + t` for `t` from 0 to 3, which is 16, 17, 18 and 19. Only 16 is valid.

**Why it is correct here.** The valid range is `0 <= i < 17`. Lanes 17, 18 and 19 exist only because the launch rounds up to whole blocks, so the tail guard `if i < n` must stop them before any load or store.

**A plausible wrong approach.** Assuming only one lane is out of range, or guarding with `i <= n`, lets index 17 through. That reads one element past the end, which may return a neighbor's data or trip a memory checker.

**How to verify.** Write the four indices with a valid or invalid mark and confirm exactly three are invalid. The reference's comprehension uses `if b*block+t < n`, the same guard, and its assertion that visits equal `range(n)` passes.

## Exercise 3: Test zero without launching

Return empty before launch.

**Approach.** Check `n == 0` in the host wrapper and return an empty output without computing a grid or launching.

**Why it is correct here.** With `n = 0` the ceiling formula gives 0 blocks. Many runtimes reject a zero-sized grid as an invalid configuration, so the empty case must be handled before the launch, and the correct result is simply an empty array.

**A plausible wrong approach.** Clamping the grid to at least one block avoids the launch error but runs lanes whose guard is always false. That works, but it hides the empty case inside the kernel and still pays launch overhead for no work.

**How to verify.** Call the wrapper with an empty input and assert the result is empty and that no launch was recorded, for example with a counter in a mock launcher. The CPU model should return `[]` for `n = 0` as well.

## Exercise 4: Implement grid-stride coverage

Advance by grid size times block size.

**Approach.** Write a grid-stride loop: each thread starts at its global index `t` and advances by the total number of threads, `stride = grid_size * block_size`, until it passes `n`.

**Why it is correct here.** With 6 threads and `n = 14`, thread 0 visits 0, 6, 12, thread 1 visits 1, 7, 13, and threads 2 to 5 each visit two indices. Every index in 0 to 13 is visited exactly once, which the reference checks by sorting the union.

**A plausible wrong approach.** Advancing by `block_size` instead of the total thread count makes threads in different blocks visit the same indices. The output may still look right for idempotent writes, but accumulations double count.

**How to verify.** Run the reference: `sorted(strided) == list(range(14))` is asserted. Add a check that `len(strided) == 14`, which fails if any index is visited twice.

## Exercise 5: Find floor-division data loss

Floor division omits the final partial block.

**Approach.** Look for launch code using `n // block` and replace it with ceiling division, then keep the in-kernel guard.

**Why it is correct here.** Floor division drops the remainder. For `n = 10` and `block = 4`, it launches two blocks, covering indices 0 to 7, so elements 8 and 9 are never processed.

**A plausible wrong approach.** Fixing it by launching `n // block + 1` blocks always adds a block even when `n` is a multiple of the block size. That is safe with a guard but launches an entire idle block for `n = 8`.

**How to verify.** Test `n = 10`: the output must have all ten elements processed. Test `n = 8` and confirm the ceiling formula gives exactly two blocks.

## Exercise 6: Specify a sanitizer check

Run real kernels under supported memory checking separately.

**Approach.** Specify a separate run of the real kernel under the CUDA memory checker (`compute-sanitizer`) with a tail size such as `n = 17`, and record its report alongside the CPU model result.

**Why it is correct here.** The CPU model proves the index arithmetic covers the range. It cannot detect an out-of-bounds access in compiled code, which is exactly what a missing tail guard causes.

**A plausible wrong approach.** Treating the passing CPU model as proof that the kernel is memory safe confuses the model of the formula with the code a compiler generated.

**How to verify.** Run the sanitizer on a device with the guard removed to see it report invalid accesses, then with the guard restored to see a clean report. Without a device, mark this check as not attempted.

## Reference observation

Every valid index appears exactly once.

The reference file is `courses/cuda/python/references/cuda-074_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
