# cuda-014: explanatory solutions

## Mechanism review

A one-dimensional launch gives a thread the starting index blockIdx.x*blockDim.x+threadIdx.x. A grid-stride loop advances that index by blockDim.x*gridDim.x until it reaches n. Every nonnegative index has one remainder modulo the positive stride, so exactly one starting thread owns it. Cast to a sufficiently wide integer before multiplying dimensions; widening after an overflow is too late. Ceiling division supplies enough threads for one-element mapping, but a grid-stride loop also allows a bounded grid to cover a much larger input. A bounds test is required even when most demonstration sizes divide evenly.

The separate [CPU reference](../references/cuda-014_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Use two blocks of four threads for \(\mathrm{n}=19\). Thread 0 owns indices 0,8,16; thread 1 owns 1,9,17; thread 2 owns 2,10,18; thread 3 owns 3,11. Every element has exactly one owner. This ownership trace is CPU reasoning, not a simulator of warp scheduling or GPU timing.

## Exercise 2

For x=\([0,1,2,3,4]\) and y=\([5,4,3,2,1]\), vector addition returns five fives. Extend the fixture to \(\mathrm{n}=33\) with distinct values to expose a tail just beyond a warp boundary. Test empty, singleton and a larger odd prime as well.

## Exercise 3

The indices are 5,13,21. The next value 29 is outside the range.

## Exercise 4

Index n lies one past the final element. A sentinel or sanitizer may catch it; lengths 1 and 33 make small useful reproducers.

## Exercise 5

Two blocks, with 31 inactive thread positions in the second block. Guard every output access.

## Exercise 6

Compute a local bounded index first, then add a validated chunk offset. Preserve both local capacity and global destination bounds.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-014_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Compute a local bounded index first, then add a validated chunk offset. Preserve both local capacity and global destination bounds.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
