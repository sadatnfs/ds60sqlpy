# cuda-105: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute barrier time

The slowest rank controls the barrier.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute barrier time** is qualified there.

## Exercise 2: Compare parallelism types

Separate model replication and operation/layer/state partition.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare parallelism types** is qualified there.

## Exercise 3: Diagnose a missing rank

Bound waits and stop the owned job.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **diagnose a missing rank** is qualified there.

## Exercise 4: Define checkpoint consistency

Use a documented common update boundary.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define checkpoint consistency** is qualified there.

## Exercise 5: Budget communication

Count bytes and frequency per collective.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **budget communication** is qualified there.

## Exercise 6: Design owned-host cleanup

Terminate only declared job resources and preserve checkpoints.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design owned-host cleanup** is qualified there.

## Reference observation

Barrier 30 ms; mixed-step checkpoint rejected.

The reference file is `courses/cuda/python/references/cuda-105_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
