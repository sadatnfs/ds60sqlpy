# cuda-023: explanatory solutions

## Mechanism review

A stencil computes each output from a neighborhood of input values. The boundary policy is part of the mathematics: clamped, periodic and fixed-zero boundaries describe different problems. Use separate input and output buffers for a time step so one update cannot change a neighbor's inputs halfway through the step. A tiled implementation loads a halo around its interior region because edge outputs need values from neighboring tiles. A barrier only protects data loaded by the same cooperating group; it does not legalize global in-place updates across independently scheduled blocks.

The separate [CPU reference](../references/cuda-023_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For \([2,4,8]\) with a three-point mean and fixed-zero outside values, one step gives \([2,\frac{14}{3},4]\). With clamped boundaries it gives \([\frac{8}{3},\frac{14}{3},\frac{20}{3}]\). Both are valid calculations, but they answer different questions. A reference must match the chosen policy.

**Approach:** Average each point with its two neighbors, substituting zero for indices -1 and 3 in [2, 4, 8].

**Why it is correct:** Index 0 sees 0 + 2 + 4 = 6 for mean 2, index 2 sees 4 + 8 + 0 for mean 4, and the middle sees 14 / 3.

**A plausible wrong approach:** Clamping silently while the spec says fixed-zero gives [8/3, 14/3, 20/3], a correct answer to a different question.

**How to verify:** The reference asserts out == [2.0, 14 / 3, 4.0] and that the input is still [2.0, 4.0, 8.0] afterward.

## Exercise 2

An in-place left-to-right update reads newly computed values for later neighbors, creating a directional bias. Two-buffer updates read only the original row and swap roles after completion. For multiple GPU steps, preserve the dependency between launches or streams before swapping logical roles.

**Approach:** Read from the original buffer and write to a second one, swapping roles between steps or launches.

**Why it is correct:** Each output then depends only on the previous state, which matches the mathematical update for every index at once.

**A plausible wrong approach:** Updating in place left to right means index 1 reads the already smoothed index 0, which biases the result toward one direction.

**How to verify:** Run one step both ways on [2, 4, 8] and confirm only the two-buffer version matches the reference values.

## Exercise 3

Every three-element neighborhood contains all three values, so each output is \(\frac{14}{3}\).

**Approach:** Wrap index -1 to 2 and index 3 to 0 so each neighborhood includes all three values.

**Why it is correct:** With three elements every window is a permutation of 2, 4 and 8, so each mean is 14 / 3.

**A plausible wrong approach:** Applying the fixed-zero rule while calling it periodic gives 2 and 4 at the ends instead.

**How to verify:** Check all three outputs equal 14 / 3 within float tolerance and that their sum equals the input sum 14.

## Exercise 4

Compare the documented boundary policy, halo loading and row stride before changing the smoothing formula or tolerance.

**Approach:** Compare the edge rows against the documented policy, then inspect halo loads and the row stride.

**Why it is correct:** Interior agreement with edge disagreement points at boundary handling rather than the averaging formula.

**A plausible wrong approach:** Loosening the tolerance until the test passes hides a halo or padding bug that will grow with image size.

**How to verify:** Diff the output against the reference only on the first and last rows and columns and look for a pattern.

## Exercise 5

(\(0+6+0\))/\(3=2\) under the stated mean. A clamped rule instead returns six.

**Approach:** Apply the radius-one mean with zeros outside: (0 + 6 + 0) / 3.

**Why it is correct:** Both neighbors of the only element are outside the array, so they contribute zero.

**A plausible wrong approach:** Returning 6 because the array has no neighbors silently switches to the clamped rule.

**How to verify:** Assert the fixed-zero result is 2 and the clamped result is 6 as separate cases.

## Exercise 6

Define timestep and stability assumptions, separate old/new fields, exchange halos where needed and check an appropriate conservation or monotonicity property.

**Approach:** Fix the timestep, keep old and new fields separate, exchange halos each step and check a conserved quantity.

**Why it is correct:** Explicit diffusion is stable only under a step size bound, and conservation catches lost boundary flux.

**A plausible wrong approach:** Running many steps in place in one kernel without a grid-wide dependency lets blocks read neighbors from the wrong step.

**How to verify:** Track the total over steps under periodic boundaries and confirm it stays constant within rounding.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-023_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Define timestep and stability assumptions, separate old/new fields, exchange halos where needed and check an appropriate conservation or monotonicity property.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
