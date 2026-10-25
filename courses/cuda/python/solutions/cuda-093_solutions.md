# cuda-093: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count specializations

Two distinct shape signatures.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count specializations** is qualified there.

## Exercise 2: Calculate break-even calls

At 500 calls costs tie and 501 starts benefiting.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate break-even calls** is qualified there.

## Exercise 3: Describe a graph break

Unsupported dynamic behavior can leave compiled regions.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **describe a graph break** is qualified there.

## Exercise 4: Specify an accepted shape set

List bounded dimensions and dtypes.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify an accepted shape set** is qualified there.

## Exercise 5: Compare gradients

Forward agreement does not imply backward agreement.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare gradients** is qualified there.

## Exercise 6: Separate compilation and replay

Compilation creates code while replay reuses an execution schedule.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate compilation and replay** is qualified there.

## Reference observation

Two modeled specializations;500-call break-even.

The reference file is `courses/cuda/python/references/cuda-093_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
