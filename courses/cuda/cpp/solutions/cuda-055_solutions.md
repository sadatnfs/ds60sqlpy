# cuda-055: explanatory solutions

## Mechanism review

Cooperative Groups makes participating thread groups explicit. A group collective is valid only when its membership and participation requirements are met. A block group can express block cooperation; a grid-wide group requires a supported cooperative launch and launch-size constraints. Ordinary launches cannot safely turn a hand-written spin loop into a global barrier. Device support, resource usage and residency determine whether a cooperative grid fits. Start with block-level algorithms and keep a multi-kernel fallback whose dependencies are established by normal launch ordering.

The separate [CPU reference](../references/cuda-055_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

An eight-thread conceptual block splits into two groups of four. Each group sums its values: \([1,2,3,4]\) gives ten and \([5,6,7,8]\) gives 26. The block-level final result is 36 after a separate valid combination step. Group-local synchronization does not synchronize the other group automatically.

**Approach:** Split eight threads into two groups of four, sum each group, then combine in a separate step.

**Why it is correct:** Group sums are 10 and 26, and their combination is 36.

**A plausible wrong approach:** Assuming a group sync also orders the other group skips the combination step's ordering.

**How to verify:** The reference asserts partials == [10, 26] and their sum is 36.

## Exercise 2

A simplified cooperative capacity is four SMs times two resident blocks per SM, or eight blocks. Requesting twelve cooperative blocks violates that assumed capacity. The actual supported limit must be obtained for the real kernel/device; source-level arithmetic is only an explanatory model.

**Approach:** Multiply four SMs by two blocks per SM for a modeled capacity of eight.

**Why it is correct:** Twelve cooperative blocks exceed eight, so the launch is invalid under this model.

**A plausible wrong approach:** Launching twelve and hoping some finish early can deadlock at the grid barrier.

**How to verify:** Query the real occupancy API for the kernel and device before launch.

## Exercise 3

A group defines participants; input count defines valid data. Tail participants may contribute neutral values while still honoring collective participation.

**Approach:** Separate the group's participants from the valid input count.

**Why it is correct:** Tail participants still join collectives but contribute neutral values.

**A plausible wrong approach:** Removing tail threads from the group breaks the collective's membership.

**How to verify:** Test an input of five with groups of four and check the sum.

## Exercise 4

There is no guarantee all needed blocks are resident or progress together. Use the supported cooperative contract or separate stages.

**Approach:** Use a cooperative launch or split the work into separate kernels.

**Why it is correct:** Ordinary launches do not guarantee all blocks are resident together.

**A plausible wrong approach:** Calling a grid barrier in an ordinary launch can wait on unscheduled blocks forever.

**How to verify:** Run the multi-kernel version and compare outputs.

## Exercise 5

Keep the reading model and a correct multi-kernel fallback; mark the optional cooperative execution unsupported.

**Approach:** Keep a correct multi-kernel fallback and mark cooperative execution unsupported.

**Why it is correct:** Learners still get a correct result and the model.

**A plausible wrong approach:** Failing the whole lesson when the feature is missing removes a working path.

**How to verify:** Run on a device without support and confirm the fallback runs.

## Exercise 6

Define tile membership, neutralize tails, perform group-local combination and then a separately ordered global combination without hidden participation assumptions.

**Approach:** Define tile groups, neutralize tails, reduce per group, then combine globally in an ordered step.

**Why it is correct:** Explicit groups make participation visible.

**A plausible wrong approach:** Assuming all threads participate when some are tails hides incorrect data.

**How to verify:** Compare with a host sum for ragged sizes.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-055_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Define tile membership, neutralize tails, perform group-local combination and then a separately ordered global combination without hidden participation assumptions.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
