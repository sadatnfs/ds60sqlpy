# cuda-023: explanatory solutions

## Mechanism review

A stencil computes each output from a neighborhood of input values. The boundary policy is part of the mathematics: clamped, periodic and fixed-zero boundaries describe different problems. Use separate input and output buffers for a time step so one update cannot change a neighbor's inputs halfway through the step. A tiled implementation loads a halo around its interior region because edge outputs need values from neighboring tiles. A barrier only protects data loaded by the same cooperating group; it does not legalize global in-place updates across independently scheduled blocks.

The separate [CPU reference](../references/cuda-023_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For \([2,4,8]\) with a three-point mean and fixed-zero outside values, one step gives \([2,\frac{14}{3},4]\). With clamped boundaries it gives \([\frac{8}{3},\frac{14}{3},\frac{20}{3}]\). Both are valid calculations, but they answer different questions. A reference must match the chosen policy.

## Exercise 2

An in-place left-to-right update reads newly computed values for later neighbors, creating a directional bias. Two-buffer updates read only the original row and swap roles after completion. For multiple GPU steps, preserve the dependency between launches or streams before swapping logical roles.

## Exercise 3

Every three-element neighborhood contains all three values, so each output is \(\frac{14}{3}\).

## Exercise 4

Compare the documented boundary policy, halo loading and row stride before changing the smoothing formula or tolerance.

## Exercise 5

(\(0+6+0\))/\(3=2\) under the stated mean. A clamped rule instead returns six.

## Exercise 6

Define timestep and stability assumptions, separate old/new fields, exchange halos where needed and check an appropriate conservation or monotonicity property.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-023_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Define timestep and stability assumptions, separate old/new fields, exchange halos where needed and check an appropriate conservation or monotonicity property.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
