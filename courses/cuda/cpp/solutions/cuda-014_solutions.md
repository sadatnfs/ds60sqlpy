# cuda-014: explanatory solutions

## Mechanism review

A one-dimensional launch gives a thread the starting index blockIdx.x*blockDim.x+threadIdx.x. A grid-stride loop advances that index by blockDim.x*gridDim.x until it reaches n. Every nonnegative index has one remainder modulo the positive stride, so exactly one starting thread owns it. Cast to a sufficiently wide integer before multiplying dimensions; widening after an overflow is too late. Ceiling division supplies enough threads for one-element mapping, but a grid-stride loop also allows a bounded grid to cover a much larger input. A bounds test is required even when most demonstration sizes divide evenly.

## Exercise 1

Use two blocks of four threads for \(\mathrm{n}=19\). Thread 0 owns indices 0,8,16; thread 1 owns 1,9,17; thread 2 owns 2,10,18; thread 3 owns 3,11. Every element has exactly one owner. This ownership trace is CPU reasoning, not a simulator of warp scheduling or GPU timing.

**Approach:** Set stride to the total thread count 2 * 4 = 8 and list i, i + 8, i + 16 below 19 for each thread.

**Why it is correct:** Indices congruent to t modulo 8 belong to thread t only, so the eight lists partition 0 to 18.

**A plausible wrong approach:** Using blockDim.x = 4 as the stride makes block 1 revisit indices block 0 already owns.

**How to verify:** The reference asserts the sorted union equals range(19) with 19 unique entries, and thread 0 owns [0, 8, 16].

## Exercise 2

For x=\([0,1,2,3,4]\) and y=\([5,4,3,2,1]\), vector addition returns five fives. Extend the fixture to \(\mathrm{n}=33\) with distinct values to expose a tail just beyond a warp boundary. Test empty, singleton and a larger odd prime as well.

**Approach:** Add [0, 1, 2, 3, 4] and [5, 4, 3, 2, 1], then repeat with 33 distinct values and empty and singleton inputs.

**Why it is correct:** Every pair sums to five, and 33 places one element past the first 32-lane warp.

**A plausible wrong approach:** Testing only with five elements never crosses a block or warp edge, so a dropped tail stays hidden.

**How to verify:** Compare all 33 outputs with a host loop and confirm index 32 holds its own distinct sum.

## Exercise 3

The indices are 5,13,21. The next value 29 is outside the range.

**Approach:** Start at 5 and add stride 8 while the index stays below 22.

**Why it is correct:** 5 + 8 = 13 and 13 + 8 = 21 are valid, while 29 exceeds the bound.

**A plausible wrong approach:** Stopping at i <= n would admit 22 if it appeared, one past the last element.

**How to verify:** Run list(range(5, 22, 8)) and expect [5, 13, 21].

## Exercise 4

Index n lies one past the final element. A sentinel or sanitizer may catch it; lengths 1 and 33 make small useful reproducers.

**Approach:** Change the comparison to i < n so the last valid index is n minus one.

**Why it is correct:** Arrays of length n hold indices 0 through n - 1; index n is outside the allocation.

**A plausible wrong approach:** Allocating n + 1 elements hides the write but leaves the logical contract broken.

**How to verify:** Place a sentinel after a length-1 buffer and confirm it survives the fixed kernel.

## Exercise 5

Two blocks, with 31 inactive thread positions in the second block. Guard every output access.

**Approach:** Compute ceil(33 / 32) = 2 blocks and count unused positions in the second.

**Why it is correct:** The second block covers indices 32 to 63, where only index 32 is valid, leaving 31 idle.

**A plausible wrong approach:** Using 33 / 32 with integer division gives one block and loses element 32.

**How to verify:** Evaluate (33 + 31) / 32 in integer arithmetic and expect 2.

## Exercise 6

Compute a local bounded index first, then add a validated chunk offset. Preserve both local capacity and global destination bounds.

**Approach:** Bound the local index by chunk length, then add the chunk offset and check the global bound.

**Why it is correct:** Both limits matter: the chunk buffer has its own capacity and the destination has its own length.

**A plausible wrong approach:** Adding the offset first and checking only the global bound can overrun a shorter final chunk.

**How to verify:** Test a final chunk shorter than the rest and confirm no write past its local capacity.

## Self-check answers

1. **In worked example 1, why does thread 3 own only two indices?** Its next index, 19, equals n, so the loop stops after 3 and 11.
2. **Why cast to a wide integer before multiplying block index by block size?** The product can overflow a 32-bit int for large grids, and widening after the overflow cannot recover the lost value.
3. **What does a grid-stride loop give you that a one-element mapping does not?** Correct coverage of any n with a fixed grid size, so the launch need not grow with the input.

## Numerical reference and its limits

The [CPU reference](../references/cuda-014_cpu.py) reproduces worked example 1 and prints `{'thread_0': [0, 8, 16], 'all_elements_written_once': True}`.

## Transfer review

Compute a local bounded index first, then add a validated chunk offset. Preserve both local capacity and global destination bounds.
