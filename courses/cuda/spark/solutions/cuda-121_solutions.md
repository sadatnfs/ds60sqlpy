# cuda-121: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate duplicate join output

Multiply key multiplicities.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate duplicate join output** is qualified there.

## Exercise 2: Add unmatched keys

Inner joins exclude unmatched keys while outer joins preserve defined null rows.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **add unmatched keys** is qualified there.

## Exercise 3: Identify skew

Compare maximum and distribution not average alone.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **identify skew** is qualified there.

## Exercise 4: Compare broadcast and shuffle

Broadcast replicates one side and shuffle redistributes both as needed.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare broadcast and shuffle** is qualified there.

## Exercise 5: Design a safe rewrite

Preserve duplicates and null-key semantics.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a safe rewrite** is qualified there.

## Exercise 6: Inspect final AQE decision

Capture executed plan after action.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **inspect final AQE decision** is qualified there.

## Reference observation

Four A matches from two-by-two duplicate keys.

The reference file is `courses/cuda/spark/references/cuda-121_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
