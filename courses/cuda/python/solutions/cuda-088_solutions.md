# cuda-088: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute serial time

Sum stage times.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute serial time** is qualified there.

## Exercise 2: Compute an ideal bottleneck bound

The slowest stage limits steady state.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute an ideal bottleneck bound** is qualified there.

## Exercise 3: Budget the queue

Multiply batch payload by queue depth.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **budget the queue** is qualified there.

## Exercise 4: Explain pinned versus ordinary host storage

Pinning affects transfer behavior and host resources.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain pinned versus ordinary host storage** is qualified there.

## Exercise 5: Compare resident-data diagnostic

It isolates input cost without proving production throughput.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare resident-data diagnostic** is qualified there.

## Exercise 6: Choose bounded worker experiments

Vary one worker or queue setting at a time.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose bounded worker experiments** is qualified there.

## Reference observation

Serial 10 ms, ideal steady-state 6 ms, queued payload 25165824 bytes.

The reference file is `courses/cuda/python/references/cuda-088_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
