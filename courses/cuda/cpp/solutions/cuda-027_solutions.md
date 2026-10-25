# cuda-027: explanatory solutions

## Mechanism review

Warp collectives require agreement about participating lanes. A mask names lanes expected to take part in a synchronized intrinsic, and source lanes used by a shuffle must actually participate. Independent thread scheduling means a convenient source ordering is not a general synchronization guarantee. Partial warps and divergent predicates need explicit reasoning. One safe educational reduction pattern has all lanes in a full warp participate, assigns zero to invalid data lanes, and then uses a full mask. A genuinely partial group needs a suitable mask and algorithm, not the same mask pasted everywhere.

The separate [CPU reference](../references/cuda-027_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Eight selected lanes among a full 32-thread warp contribute values 1 through 8; other lanes contribute zero. All 32 lanes execute the collective, giving sum 36. This is different from launching only eight threads and pretending the absent 24 lanes participate.

## Exercise 2

A ballot for predicates true at lanes 0,2 and 5 has bit mask 37: binary positions contribute \(1+4+32\). Population count is three. Reading a shuffled value from lane seven is not justified if lane seven is outside the participating group.

## Exercise 3

The bits contribute \(2+8+16=26\); the selected-lane count is three.

## Exercise 4

The mask names lanes that do not execute the collective. Reorganize participation or use a correctly defined group and algorithm.

## Exercise 5

Every data contribution is zero and the reduction is zero; participation and data selection are different concepts.

## Exercise 6

Define membership separately for each segment, ensure each collective's source/destination lanes belong to the group and test segments crossing warp boundaries.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-027_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Define membership separately for each segment, ensure each collective's source/destination lanes belong to the group and test segments crossing warp boundaries.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
