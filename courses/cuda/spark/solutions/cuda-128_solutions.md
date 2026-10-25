# cuda-128: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute end-to-end tradeoff

Sum all changed costs.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute end-to-end tradeoff** is qualified there.

## Exercise 2: Choose a tiny-data tool

A local CPU tool may be sufficient.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a tiny-data tool** is qualified there.

## Exercise 3: Separate setup and steady state

Both boundaries matter for user workflow.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate setup and steady state** is qualified there.

## Exercise 4: Include operational cost

Count maintenance compatibility and resource ownership.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **include operational cost** is qualified there.

## Exercise 5: Define a reevaluation trigger

Name data growth or changed workload support.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define a reevaluation trigger** is qualified there.

## Exercise 6: Write an evidence-based recommendation

Recommend the simplest qualified option and state missing evidence.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **write an evidence-based recommendation** is qualified there.

## Reference observation

GPU candidate adds 10 modeled seconds end to end.

The reference file is `courses/cuda/spark/references/cuda-128_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
