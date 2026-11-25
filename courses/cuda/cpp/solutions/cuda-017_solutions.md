# cuda-017: explanatory solutions

## Mechanism review

Shared memory lets threads in one block communicate through a common scratch array. Communication requires ordering: a consumer must not read a location until its producer has written it. `__syncthreads()` is a block barrier with memory-ordering effects for participating threads. Put bounds predicates around loads and stores while keeping the required barrier participation uniform. Invalid tail lanes can load a neutral value and still reach the barrier. A barrier does not coordinate ordinary independent blocks, and a memory fence does not force other threads to arrive at the same program point.

## Exercise 1

Four threads load \([3,6,9,12]\) into a shared tile, synchronize, then thread t reads tile[3-t]. The reversed output is \([12,9,6,3]\). Without the barrier, a consumer could read before another thread loads its value. An apparent success on one execution is not a synchronization proof.

**Approach:** Load [3, 6, 9, 12] into the tile, synchronize, then read tile[3 - t].

**Why it is correct:** The barrier guarantees every load completes before any thread reads another's slot.

**A plausible wrong approach:** Dropping the barrier because one test run gave [12, 9, 6, 3] trusts luck over a guarantee.

**How to verify:** The reference asserts the reversal [12, 9, 6, 3]; run racecheck on a GPU for evidence.

## Exercise 2

For a three-element tail in a four-thread block, lane three loads a neutral zero and still participates in the barrier. Only valid lanes store output. A conditional `if (i<n) { load; barrier; }` can violate the barrier contract when some block threads skip it.

**Approach:** Load zero for lane three, have all four threads reach the barrier, store only valid lanes.

**Why it is correct:** Every thread in the block must reach __syncthreads, and zero adds nothing to the sum.

**A plausible wrong approach:** Wrapping both the load and the barrier in if (i < n) leaves lane three skipping it.

**How to verify:** The reference asserts the neutralized sum is 18 for [3, 6, 9, 0].

## Exercise 3

Thread three produces tile\([3]\), the barrier establishes availability, and thread zero consumes it.

**Approach:** Trace output 0: it reads tile[3], which thread 3 wrote before the barrier.

**Why it is correct:** The barrier orders thread 3's store before thread 0's load.

**A plausible wrong approach:** Assuming thread 0 wrote tile[3] confuses output ownership with input ownership.

**How to verify:** Label every producer-consumer pair and confirm each crosses the barrier.

## Exercise 4

Move the required barrier outside the bounds condition, neutralize invalid loads and predicate only accesses that need valid indices.

**Approach:** Move __syncthreads outside the bound check and load a neutral value for invalid lanes.

**Why it is correct:** All threads then reach the barrier, and invalid lanes contribute harmless values.

**A plausible wrong approach:** Adding a second barrier inside the else branch still splits threads across two distinct barriers.

**How to verify:** Run a ragged size such as 3 and confirm completion and correct output.

## Exercise 5

Other blocks do not participate. Use separate dependent kernel stages or a qualified cooperative launch design.

**Approach:** Explain that __syncthreads orders only threads in one block.

**Why it is correct:** Blocks may run at different times, so a block barrier cannot wait for them.

**A plausible wrong approach:** Spinning on a global flag for other blocks can deadlock when those blocks are not resident.

**How to verify:** Split the reduction into two kernels and validate the final sum on the host.

## Exercise 6

Name owners for interior and halo loads, synchronize before consumption, define boundary values and keep output separate from input.

**Approach:** Assign interior loads to their own threads and halo loads to edge threads, then synchronize.

**Why it is correct:** Each neighbor value must be in the tile before any average reads it.

**A plausible wrong approach:** Writing averages back into the input tile lets neighbors read already-updated values.

**How to verify:** Compare tile results with a host stencil, including edges with the defined boundary.

## Self-check answers

1. **In worked example 1, which thread produces the value read by thread 0?** Thread 3, which loaded 12 into tile[3].
2. **Why must tail lanes still reach the barrier?** A block barrier expects every thread of the block; skipping it is undefined and can hang.
3. **What neutral value suits a max operation in a padded tile?** The lowest representable value, such as negative infinity for floats.

## Numerical reference and its limits

The [CPU reference](../references/cuda-017_cpu.py) reproduces worked example 1 and prints `{'reversal': [12, 9, 6, 3], 'neutralized_tail_sum': 18}`.

## Transfer review

Name owners for interior and halo loads, synchronize before consumption, define boundary values and keep output separate from input.
