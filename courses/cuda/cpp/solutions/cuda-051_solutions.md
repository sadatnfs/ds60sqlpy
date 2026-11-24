# cuda-051: explanatory solutions

## Mechanism review

Softmax converts a row of logits into nonnegative weights that sum to one. Exponentiating large logits directly can overflow even when the final probabilities are ordinary finite values. Subtracting the row maximum preserves the exact mathematical ratios while keeping the largest exponential at one. A kernel needs a maximum reduction, exponentials, a sum reduction and division, with correct row boundaries and accumulation precision. Define behavior for masks and exceptional inputs separately; an all-masked row cannot be treated as an ordinary finite row without a policy. Test short, ragged and extreme-valued rows.

The separate [CPU reference](../references/cuda-051_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

For logits \([1000,1001]\), subtract maximum 1001 to obtain \([-1,0]\). Exponentials are approximately \([0.367879,1]\), giving probabilities \([0.268941,0.731059]\). Directly computing \(e^{1001}\) can overflow in common floating types although the normalized answer is well behaved.

**Approach:** Subtract the row maximum 1001 from [1000, 1001] to get [-1, 0], exponentiate, and divide by the sum.

**Why it is correct:** Softmax is unchanged by subtracting a constant, and e^-1 / (e^-1 + 1) gives 0.268941 while 1 / (e^-1 + 1) gives 0.731059.

**A plausible wrong approach:** Calling exp(1001) directly overflows to infinity in float32 or float64, and infinity divided by infinity yields NaN.

**How to verify:** The reference asserts the sum is within 1e-12 of one and p[1] is within 1e-12 of 0.7310585786300049.

## Exercise 2

For \([4,4,4]\), subtracting four produces three zeros, so each probability is one third. For a single finite logit, the output is one. These cases check normalization and row handling independently of large exponentials.

**Approach:** Run [4, 4, 4] and a single-element row through the same kernel as distinct fixtures.

**Why it is correct:** Equal logits subtract to zeros, giving three ones over a sum of three, so each probability is one third; a single logit gives exactly one.

**A plausible wrong approach:** Testing only the large-logit case checks overflow handling but not that each row divides by its own sum.

**How to verify:** The reference asserts softmax([4, 4, 4]) == [1 / 3] * 3; also assert a singleton returns [1.0].

## Exercise 3

\([0.5,0.5]\), with each entry nonnegative and the sum one.

**Approach:** Subtract the maximum 0 from [0, 0] and normalize two ones.

**Why it is correct:** Each exponential is 1 and the sum is 2, so each probability is 0.5.

**A plausible wrong approach:** Dividing by the row length instead of the exponential sum gives the same result here and hides that bug.

**How to verify:** Assert [0.5, 0.5] and also test [0, 1] where the two formulas differ.

## Exercise 4

Normalization is only an invariant. Compare every entry with a reference using distinct logits and preserve positional meaning.

**Approach:** Compare every entry against a reference on logits with distinct values.

**Why it is correct:** A permuted output still sums to one, so the sum check cannot detect it.

**A plausible wrong approach:** Adding more rows that check only the sum keeps missing positional errors entirely.

**How to verify:** Use logits [1, 2, 3] and confirm the largest probability is in the last column.

## Exercise 5

Follow an explicit model policy such as rejection or a defined zero-output convention; avoid an unexamined infinity-minus-infinity calculation.

**Approach:** Choose a policy for all-masked rows, such as rejection or zero output, and implement it before max-subtraction.

**Why it is correct:** Every logit is negative infinity, so the max is negative infinity and subtracting gives infinity minus infinity.

**A plausible wrong approach:** Letting the ordinary path run produces NaN that spreads through later layers.

**How to verify:** Feed a fully masked row and assert the chosen policy output with no NaN.

## Exercise 6

State supported row widths, strides, dtype, accumulation, masks and finite-input policy, then test extremes and tails before timing.

**Approach:** State row widths, strides, dtype, accumulation precision, masks and finite-input policy for the fused kernel.

**Why it is correct:** These choices fix what the kernel must compute before speed matters.

**A plausible wrong approach:** Timing a fused kernel before testing extreme logits and ragged tails can reward a wrong one.

**How to verify:** Test large logits, masks and tail widths against the reference before timing.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-051_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State supported row widths, strides, dtype, accumulation, masks and finite-input policy, then test extremes and tails before timing.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
