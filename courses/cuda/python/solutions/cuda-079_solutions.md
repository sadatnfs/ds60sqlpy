# cuda-079: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count touched segments

Count distinct integer offsets divided by segment size.

**Approach.** Apply the simplified rule: divide each byte offset by the 32-byte segment width with integer division and count the distinct quotients. Offsets `0, 4, ..., 28` all give quotient 0, so one segment is touched.

**Why it is correct here.** Within this model a memory transaction moves an aligned 32-byte segment, so eight 4-byte loads that fall inside one segment cost one transaction. The `segments` helper implements exactly the set-of-quotients rule.

**A plausible wrong approach.** Counting one transaction per lane, eight here, treats every load as independent and ignores coalescing. That would make the contiguous and strided patterns look equally expensive.

**How to verify.** Call `segments([4*i for i in range(8)])` and confirm 1; call it on `[32*i for i in range(8)]` and confirm 8. Label both numbers as model outputs, not profiler counters.

## Exercise 2: Shift the base by four bytes

The shift may cross a boundary.

**Approach.** Shift the contiguous offsets by four bytes, giving `4, 8, ..., 32`, and recount: offsets 4 to 28 have quotient 0 and offset 32 has quotient 1, so two segments are touched.

**Why it is correct here.** Only the last lane crosses the aligned boundary at byte 32, but that is enough to require a second segment. Alignment of the base address matters even when the access is perfectly contiguous.

**A plausible wrong approach.** Assuming contiguity alone guarantees one segment ignores the boundary. A misaligned base can double the modeled transactions for the same amount of useful data.

**How to verify.** Compute `segments([4 + 4*i for i in range(8)])` and confirm 2. A shift of 0 or 32 bytes keeps the count at 1, which checks that only misalignment causes the change.

## Exercise 3: Model a stride of two

Stride can increase transaction count.

**Approach.** Model a stride of two elements: offsets `0, 8, ..., 56`. Integer division by 32 yields quotients 0 and 1, so two segments are touched to deliver 32 useful bytes.

**Why it is correct here.** Half the bytes in each fetched segment are unused, so the useful fraction drops to one half. Larger strides keep spreading lanes until each one touches its own segment, as the 32-byte stride shows.

**A plausible wrong approach.** Thinking stride only matters when it reaches the segment size misses the intermediate cost. Stride two already doubles the transactions in this model.

**How to verify.** Compute segments for strides 1, 2, 4 and 8 elements and confirm counts 1, 2, 4 and 8. The trend must be monotone for these aligned offsets.

## Exercise 4: Explain tiled transpose

Shared storage rearranges cooperative ownership.

**Approach.** Explain a tiled transpose: a block loads a tile with row-contiguous reads into a shared array, synchronizes, then writes the tile out with row-contiguous writes in the transposed position, reading shared memory by column.

**Why it is correct here.** A naive transpose has either reads or writes with a stride of the matrix width. Staging through shared memory makes both global accesses contiguous, while the strided part happens in fast on-chip storage. The mathematical result is unchanged.

**A plausible wrong approach.** Expecting the shared-memory version to change the output values, or to need a different verification, confuses reorganized traffic with a different algorithm.

**How to verify.** Compare the tiled result with `numpy.transpose` on a non-square matrix such as 3 by 5, including partial tiles. The outputs must be equal exactly.

## Exercise 5: Separate occupancy from throughput

More resident work can still compete for resources.

**Approach.** Separate occupancy, the number of resident warps relative to the maximum, from throughput, the useful work per second. Raising occupancy helps hide latency only when warps are waiting on memory and resources allow.

**Why it is correct here.** More resident warps also share registers, shared memory and memory bandwidth. A kernel that already saturates bandwidth gains nothing from more warps, and register pressure can force spills that slow it down.

**A plausible wrong approach.** Treating the occupancy number as the performance goal leads to changes that raise the percentage while total runtime stays the same or rises.

**How to verify.** In a profiler, record achieved occupancy together with memory throughput and runtime for two block sizes. Only the runtime of a correct output decides which is better.

## Exercise 6: Propose a matched profiler experiment

Hold dtype shape and output fixed and inspect real counters.

**Approach.** Design a profiler experiment that compares contiguous and strided kernels with the same dtype, element count, output and launch configuration, collecting real memory transaction and throughput counters.

**Why it is correct here.** Holding everything else fixed isolates the access pattern as the cause. The CPU segment model predicts a direction, and only hardware counters can confirm it.

**A plausible wrong approach.** Comparing kernels that differ in dtype or element count mixes several causes. A float64 strided kernel against a float32 contiguous one cannot attribute the difference to stride.

**How to verify.** Before reading counters, check both kernels produce the same output. Record GPU model, driver and profiler versions; without a GPU, report the experiment as designed but not run.

## Reference observation

Simplified segment counts 1 and 8, not hardware measurements.

The reference file is `courses/cuda/python/references/cuda-079_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
