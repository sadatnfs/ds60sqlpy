# cuda-020: explanatory solutions

## Mechanism review

A reduction combines values with an operation and identity. A tree reduces dependency depth compared with a serial chain, but it changes floating-point addition order. A block reduction usually first writes one partial per block; another launch combines those partials. This creates a real cross-block dependency without an unsafe grid-wide spin barrier. Tail threads contribute the identity, such as zero for addition. For a maximum, zero is not a neutral value if all inputs are negative. Define empty input explicitly and retain a higher-accuracy CPU oracle for floating-point work.

The separate [CPU reference](../references/cuda-020_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Pad \([1,2,3,4,5]\) to \([1,2,3,4,5,0,0,0]\). A halving tree produces pairwise states \([6,2,3,4]\), then \([9,6]\), then \([15]\). Each phase needs the appropriate communication ordering. Exact integer arithmetic makes ownership mistakes visible without rounding ambiguity.

## Exercise 2

For \([10^{16},1,-10^{16}]\), different valid sum trees can disagree. Compare against a compensated or higher-precision reference and report error. Do not require a GPU result to copy an arbitrary CPU association, and do not enlarge tolerance enough to hide dropped tail elements.

## Exercise 3

Negative infinity is the general floating maximum identity; zero would incorrectly dominate this entirely negative input.

## Exercise 4

Waiting blocks can occupy resources needed by unscheduled producers. Ordinary launches provide no universal simultaneous residency guarantee.

## Exercise 5

The empty sum is zero; the singleton sum equals that element. Avoid invalid zero-block launches.

## Exercise 6

Reduce both sum and count, then divide only when count is nonzero; define the empty mean policy explicitly.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-020_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Reduce both sum and count, then divide only when count is nonzero; define the empty mean policy explicitly.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
