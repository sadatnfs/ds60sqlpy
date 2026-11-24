# cuda-027: explanatory solutions

## Mechanism review

Warp collectives require agreement about participating lanes. A mask names lanes expected to take part in a synchronized intrinsic, and source lanes used by a shuffle must actually participate. Independent thread scheduling means a convenient source ordering is not a general synchronization guarantee. Partial warps and divergent predicates need explicit reasoning. One safe educational reduction pattern has all lanes in a full warp participate, assigns zero to invalid data lanes, and then uses a full mask. A genuinely partial group needs a suitable mask and algorithm, not the same mask pasted everywhere.

The separate [CPU reference](../references/cuda-027_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Eight selected lanes among a full 32-thread warp contribute values 1 through 8; other lanes contribute zero. All 32 lanes execute the collective, giving sum 36. This is different from launching only eight threads and pretending the absent 24 lanes participate.

**Approach:** Keep all 32 lanes in the collective and let the 24 unselected lanes contribute zero to the sum.

**Why it is correct:** Values 1 through 8 sum to 36 and zeros add nothing, so the full-warp reduction is correct.

**A plausible wrong approach:** Launching only eight threads and calling a full-mask shuffle names 24 lanes that never execute it.

**How to verify:** The reference asserts the 32-entry contributions sum to 36.

## Exercise 2

A ballot for predicates true at lanes 0,2 and 5 has bit mask 37: binary positions contribute \(1+4+32\). Population count is three. Reading a shuffled value from lane seven is not justified if lane seven is outside the participating group.

**Approach:** Set bit lane for lanes 0, 2 and 5 and count set bits.

**Why it is correct:** Bits 1, 4 and 32 add to 37, and three bits are set.

**A plausible wrong approach:** Shuffling from lane 7 assumes it participates, but it is outside the predicate set.

**How to verify:** The reference asserts mask == 37 and mask.bit_count() == 3.

## Exercise 3

The bits contribute \(2+8+16=26\); the selected-lane count is three.

**Approach:** Add 1 << 1, 1 << 3 and 1 << 4.

**Why it is correct:** Those bits are 2, 8 and 16, totaling 26 with three lanes selected.

**A plausible wrong approach:** Writing the lane numbers as decimal digits 1 + 3 + 4 = 8 confuses indices with bit weights.

**How to verify:** Compute bin(26) and check bits 1, 3 and 4 are set.

## Exercise 4

The mask names lanes that do not execute the collective. Reorganize participation or use a correctly defined group and algorithm.

**Approach:** Hoist the collective outside the branch or pass a mask matching only the executing lanes.

**Why it is correct:** A full mask promises all 32 lanes call the intrinsic, but only 16 do.

**A plausible wrong approach:** Adding __syncwarp before the shuffle in the branch still names absent lanes.

**How to verify:** Test with a branch taken by half the warp and confirm a correct, defined result.

## Exercise 5

Every data contribution is zero and the reduction is zero; participation and data selection are different concepts.

**Approach:** Run the full-warp collective with every contribution zero.

**Why it is correct:** All lanes participate, and the sum of zeros is zero.

**A plausible wrong approach:** Skipping the collective when no value is selected makes participation depend on data.

**How to verify:** Assert a zero result for an all-false predicate with a full mask.

## Exercise 6

Define membership separately for each segment, ensure each collective's source/destination lanes belong to the group and test segments crossing warp boundaries.

**Approach:** Define each segment's member lanes and restrict collectives to that group.

**Why it is correct:** Lanes outside a segment must not supply or receive values for it.

**A plausible wrong approach:** Using the full-warp sum for each segment mixes values from neighboring segments.

**How to verify:** Test segments that end inside a warp and one that crosses into the next warp.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-027_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Define membership separately for each segment, ensure each collective's source/destination lanes belong to the group and test segments crossing warp boundaries.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
