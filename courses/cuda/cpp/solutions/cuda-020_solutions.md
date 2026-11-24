# cuda-020: explanatory solutions

## Mechanism review

A reduction combines values with an operation and identity. A tree reduces dependency depth compared with a serial chain, but it changes floating-point addition order. A block reduction usually first writes one partial per block; another launch combines those partials. This creates a real cross-block dependency without an unsafe grid-wide spin barrier. Tail threads contribute the identity, such as zero for addition. For a maximum, zero is not a neutral value if all inputs are negative. Define empty input explicitly and retain a higher-accuracy CPU oracle for floating-point work.

The separate [CPU reference](../references/cuda-020_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Pad \([1,2,3,4,5]\) to \([1,2,3,4,5,0,0,0]\). A halving tree produces pairwise states \([6,2,3,4]\), then \([9,6]\), then \([15]\). Each phase needs the appropriate communication ordering. Exact integer arithmetic makes ownership mistakes visible without rounding ambiguity.

**Approach:** Pad five values to eight with zeros, then add element i + width into i while width halves.

**Why it is correct:** Zeros preserve the sum, and each phase halves the active values until one remains.

**A plausible wrong approach:** Padding with ones changes the total to 18 instead of 15.

**How to verify:** The reference asserts trace == [[6, 2, 3, 4], [9, 6], [15]].

## Exercise 2

For \([10^{16},1,-10^{16}]\), different valid sum trees can disagree. Compare against a compensated or higher-precision reference and report error. Do not require a GPU result to copy an arbitrary CPU association, and do not enlarge tolerance enough to hide dropped tail elements.

**Approach:** Compare the result with a compensated or wider reference and report the error.

**Why it is correct:** Different trees round differently, and both can be valid floating sums.

**A plausible wrong approach:** Requiring an exact match with sequential CPU order rejects a valid GPU tree.

**How to verify:** Compute math.fsum on the fixture and compare each tree's result to 1.0.

## Exercise 3

Negative infinity is the general floating maximum identity; zero would incorrectly dominate this entirely negative input.

**Approach:** Use negative infinity as the starting value for maximum.

**Why it is correct:** Every real value exceeds negative infinity, so the identity never wins.

**A plausible wrong approach:** Starting from zero returns 0 for an all-negative input instead of -3.

**How to verify:** Compute max([-7, -3, -9], default) with both starts and expect -3.

## Exercise 4

Waiting blocks can occupy resources needed by unscheduled producers. Ordinary launches provide no universal simultaneous residency guarantee.

**Approach:** Replace the spin wait with a second kernel launch that reads partial results.

**Why it is correct:** Waiting blocks can hold every SM while producer blocks wait to be scheduled.

**A plausible wrong approach:** Adding more waiting blocks makes the deadlock more likely, not less.

**How to verify:** Run two stages and validate the final value on the host.

## Exercise 5

The empty sum is zero; the singleton sum equals that element. Avoid invalid zero-block launches.

**Approach:** Return zero for an empty input and the element itself for a singleton.

**Why it is correct:** Zero is the additive identity and a single value needs no combination.

**A plausible wrong approach:** Launching a zero-block reduction for empty input triggers an invalid configuration.

**How to verify:** Assert sum([]) == 0 and sum([7]) == 7 in the host wrapper tests.

## Exercise 6

Reduce both sum and count, then divide only when count is nonzero; define the empty mean policy explicitly.

**Approach:** Reduce sum and count together and divide only when count is positive.

**Why it is correct:** The mean needs both quantities, and division by zero is undefined.

**A plausible wrong approach:** Dividing every partial sum by its block count averages unequal blocks wrongly.

**How to verify:** Compute the mean of [1, 2, 3, 4, 5] as 3 and test empty input.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-020_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Reduce both sum and count, then divide only when count is nonzero; define the empty mean policy explicitly.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
