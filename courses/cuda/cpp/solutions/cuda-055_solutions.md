# cuda-055: explanatory solutions

## Mechanism review

Cooperative Groups makes participating thread groups explicit. A group collective is valid only when its membership and participation requirements are met. A block group can express block cooperation; a grid-wide group requires a supported cooperative launch and launch-size constraints. Ordinary launches cannot safely turn a hand-written spin loop into a global barrier. Device support, resource usage and residency determine whether a cooperative grid fits. Start with block-level algorithms and keep a multi-kernel fallback whose dependencies are established by normal launch ordering.

The separate [CPU reference](../references/cuda-055_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

An eight-thread conceptual block splits into two groups of four. Each group sums its values: \([1,2,3,4]\) gives ten and \([5,6,7,8]\) gives 26. The block-level final result is 36 after a separate valid combination step. Group-local synchronization does not synchronize the other group automatically.

## Exercise 2

A simplified cooperative capacity is four SMs times two resident blocks per SM, or eight blocks. Requesting twelve cooperative blocks violates that assumed capacity. The actual supported limit must be obtained for the real kernel/device; source-level arithmetic is only an explanatory model.

## Exercise 3

A group defines participants; input count defines valid data. Tail participants may contribute neutral values while still honoring collective participation.

## Exercise 4

There is no guarantee all needed blocks are resident or progress together. Use the supported cooperative contract or separate stages.

## Exercise 5

Keep the reading model and a correct multi-kernel fallback; mark the optional cooperative execution unsupported.

## Exercise 6

Define tile membership, neutralize tails, perform group-local combination and then a separately ordered global combination without hidden participation assumptions.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-055_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Define tile membership, neutralize tails, perform group-local combination and then a separately ordered global combination without hidden participation assumptions.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
