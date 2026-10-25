# cuda-051: explanatory solutions

## Mechanism review

Softmax converts a row of logits into nonnegative weights that sum to one. Exponentiating large logits directly can overflow even when the final probabilities are ordinary finite values. Subtracting the row maximum preserves the exact mathematical ratios while keeping the largest exponential at one. A kernel needs a maximum reduction, exponentials, a sum reduction and division, with correct row boundaries and accumulation precision. Define behavior for masks and exceptional inputs separately; an all-masked row cannot be treated as an ordinary finite row without a policy. Test short, ragged and extreme-valued rows.

The separate [CPU reference](../references/cuda-051_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For logits \([1000,1001]\), subtract maximum 1001 to obtain \([-1,0]\). Exponentials are approximately \([0.367879,1]\), giving probabilities \([0.268941,0.731059]\). Directly computing exp(1001) can overflow in common floating types although the normalized answer is well behaved.

## Exercise 2

For \([4,4,4]\), subtracting four produces three zeros, so each probability is one third. For a single finite logit, the output is one. These cases check normalization and row handling independently of large exponentials.

## Exercise 3

\([0.5,0.5]\), with each entry nonnegative and the sum one.

## Exercise 4

Normalization is only an invariant. Compare every entry with a reference using distinct logits and preserve positional meaning.

## Exercise 5

Follow an explicit model policy such as rejection or a defined zero-output convention; avoid an unexamined infinity-minus-infinity calculation.

## Exercise 6

State supported row widths, strides, dtype, accumulation, masks and finite-input policy, then test extremes and tails before timing.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-051_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State supported row widths, strides, dtype, accumulation, masks and finite-input policy, then test extremes and tails before timing.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
