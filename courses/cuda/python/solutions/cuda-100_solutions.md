# cuda-100: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute stable softmax

Subtract the maximum first.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute stable softmax** is qualified there.

## Exercise 2: Draw a causal mask

Allow key positions no greater than query position.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **draw a causal mask** is qualified there.

## Exercise 3: Count score-matrix bytes

Batch times heads times sequence squared times itemsize.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count score-matrix bytes** is qualified there.

## Exercise 4: Define fully masked behavior

Reject or use documented zero-output behavior.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define fully masked behavior** is qualified there.

## Exercise 5: Compare fused and reference gradients

Check masks dtypes and tolerances.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare fused and reference gradients** is qualified there.

## Exercise 6: Separate backend selection from API name

Inspect supported runtime evidence rather than guessing.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate backend selection from API name** is qualified there.

## Reference observation

Stable probabilities sum to 1; lower-triangular causal mask.

The reference file is `courses/cuda/python/references/cuda-100_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
