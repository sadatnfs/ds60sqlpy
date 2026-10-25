# cuda-123: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate partition averages

Divide rows by partitions.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate partition averages** is qualified there.

## Exercise 2: Explain skew beyond averages

Report tails and maximum sizes.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain skew beyond averages** is qualified there.

## Exercise 3: Capture final AQE plan

Inspect after the action.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **capture final AQE plan** is qualified there.

## Exercise 4: Define cache policy

Use equivalent cold or warm states.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define cache policy** is qualified there.

## Exercise 5: Choose semantic and performance fixtures

Tiny bounded correctness data and representative measured data serve different purposes.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose semantic and performance fixtures** is qualified there.

## Exercise 6: Separate estimated and observed speedup

Predictions remain predictions until executed.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate estimated and observed speedup** is qualified there.

## Reference observation

Partition averages 10000 and 100000; unmatched cache states rejected.

The reference file is `courses/cuda/spark/references/cuda-123_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
