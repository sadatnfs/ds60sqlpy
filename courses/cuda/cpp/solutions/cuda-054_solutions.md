# cuda-054: explanatory solutions

## Mechanism review

Scaled dot-product attention forms scores from queries and keys, normalizes each score row with softmax and combines values using those weights. Materializing the entire score matrix costs storage proportional to sequence length squared. Tiling can avoid retaining that large intermediate by maintaining an online maximum, normalization sum and weighted output accumulator. When a new tile raises the maximum, rescale earlier accumulators before combining them. Masking and training's backward needs add contracts. A tiny educational online algorithm demonstrates memory-aware mathematics; it is not a production replacement for specialized attention libraries.

The separate [CPU reference](../references/cuda-054_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

With query \([1,0]\), keys \([[1,0],[0,1]]\) and values \([[2,0],[0,4]]\), unscaled scores are \([1,0]\). Softmax weights are approximately \([0.731059,0.268941]\), giving output \([1.462117,1.075766]\). A real scaled attention contract also divides scores by square root of key dimension.

## Exercise 2

For 4,096 tokens, a full score matrix has 16,777,216 elements per head and batch item. At four bytes each that is 64 MiB for scores alone. A tiled algorithm's advantage can come from avoiding traffic and storage, even if it recomputes some arithmetic.

## Exercise 3

The surviving probability is one, so output is \([2,0]\) under the defined valid-row policy.

## Exercise 4

Their exponential weights used the old reference maximum. Multiply old sums by exp(old_max-new_max) before combining new terms.

## Exercise 5

It must be explicitly defined and tested; ordinary max-subtraction over all negative infinity is not a valid unchecked path.

## Exercise 6

State batch/head/sequence dimensions, dtype, scaling, masks, forward/backward scope, output tolerance and memory accounting, then compare an appropriate library baseline.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-054_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

State batch/head/sequence dimensions, dtype, scaling, masks, forward/backward scope, output tolerance and memory accounting, then compare an appropriate library baseline.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
