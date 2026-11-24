# cuda-054: explanatory solutions

## Mechanism review

Scaled dot-product attention forms scores from queries and keys, normalizes each score row with softmax and combines values using those weights. Materializing the entire score matrix costs storage proportional to sequence length squared. Tiling can avoid retaining that large intermediate by maintaining an online maximum, normalization sum and weighted output accumulator. When a new tile raises the maximum, rescale earlier accumulators before combining them. Masking and training's backward needs add contracts. A tiny educational online algorithm demonstrates memory-aware mathematics; it is not a production replacement for specialized attention libraries.

The separate [CPU reference](../references/cuda-054_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

With query \([1,0]\), keys \([[1,0],[0,1]]\) and values \([[2,0],[0,4]]\), unscaled scores are \([1,0]\). Softmax weights are approximately \([0.731059,0.268941]\), giving output \([1.462117,1.075766]\). A real scaled attention contract also divides scores by square root of key dimension.

**Approach:** Score query [1, 0] against keys to get [1, 0], softmax, then weight the value rows.

**Why it is correct:** Weights 0.731059 and 0.268941 scale [2, 0] and [0, 4] to give [1.462117, 1.075766].

**A plausible wrong approach:** Skipping the 1 / sqrt(d) scaling by accident here matches the unscaled reference but breaks a scaled contract.

**How to verify:** The reference asserts the weights sum to one and prints the output pair.

## Exercise 2

For 4,096 tokens, a full score matrix has 16,777,216 elements per head and batch item. At four bytes each that is 64 MiB for scores alone. A tiled algorithm's advantage can come from avoiding traffic and storage, even if it recomputes some arithmetic.

**Approach:** Multiply 4,096 by 4,096 by 4 bytes for one head and batch item.

**Why it is correct:** That is 16,777,216 scores, or 64 MiB, before any other buffer.

**A plausible wrong approach:** Assuming a tiled kernel is faster only because of fewer FLOPs misses that it avoids this storage.

**How to verify:** The reference asserts 4096 * 4096 * 4 == 64 * 1024 * 1024.

## Exercise 3

The surviving probability is one, so output is \([2,0]\) under the defined valid-row policy.

**Approach:** Mask the second key so only the first score survives.

**Why it is correct:** One surviving weight is 1, so the output equals value row [2, 0].

**A plausible wrong approach:** Setting the masked score to 0 instead of negative infinity keeps weight on it.

**How to verify:** Assert output [2, 0] for the causal row.

## Exercise 4

Their exponential weights used the old reference maximum. Multiply old sums by \(\exp(m_{\mathrm{old}}-m_{\mathrm{new}})\) before combining new terms.

**Approach:** Multiply old sums by exp(m_old - m_new) when a new maximum appears.

**Why it is correct:** Earlier exponentials were relative to the old maximum.

**A plausible wrong approach:** Adding new terms without rescaling mixes two reference points.

**How to verify:** Compare online and full softmax over blocks where the maximum moves.

## Exercise 5

It must be explicitly defined and tested; ordinary max-subtraction over all negative infinity is not a valid unchecked path.

**Approach:** Define and test a policy for fully masked rows.

**Why it is correct:** Max-subtraction over all negative infinity yields NaN.

**A plausible wrong approach:** Letting the general path run leaves behavior undefined.

**How to verify:** Feed a fully masked row and assert the policy output.

## Exercise 6

State batch/head/sequence dimensions, dtype, scaling, masks, forward/backward scope, output tolerance and memory accounting, then compare an appropriate library baseline.

**Approach:** State batch, heads, sequence length, dtype, scaling, masks, scope, tolerance and memory accounting.

**Why it is correct:** Attention cost depends strongly on each of these.

**A plausible wrong approach:** Comparing forward-only timing with a library's forward and backward is unfair.

**How to verify:** Validate against a library baseline with matching settings before timing.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-054_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State batch/head/sequence dimensions, dtype, scaling, masks, forward/backward scope, output tolerance and memory accounting, then compare an appropriate library baseline.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
