# cuda-077: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute a tree by hand

Combine pairs and carry the leftover value.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute a tree by hand** is qualified there.

## Exercise 2: Test the odd tail

The fifth value must survive.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **test the odd tail** is qualified there.

## Exercise 3: Construct cancellation

Use large opposite signs plus a small residual.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **construct cancellation** is qualified there.

## Exercise 4: Choose absolute and relative tolerance

Near zero needs meaningful absolute tolerance.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose absolute and relative tolerance** is qualified there.

## Exercise 5: Compare atomics with staged reduction

Atomics trade simplicity for contention and order.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare atomics with staged reduction** is qualified there.

## Exercise 6: Explain deterministic settings limits

Repeatability does not imply cross-hardware identical arithmetic.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain deterministic settings limits** is qualified there.

## Reference observation

Accurate cancellation sum 1 and tail-preserving sum 15.

The reference file is `courses/cuda/python/references/cuda-077_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
