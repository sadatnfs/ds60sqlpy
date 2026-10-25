# cuda-092: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute timeline wall time

Use latest completion minus first start.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute timeline wall time** is qualified there.

## Exercise 2: Identify an overlap

Intervals sharing time overlap.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **identify an overlap** is qualified there.

## Exercise 3: Find a forced synchronization

Materializing a device scalar can wait.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **find a forced synchronization** is qualified there.

## Exercise 4: Name profiler overhead

Detailed tracing changes work and memory.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **name profiler overhead** is qualified there.

## Exercise 5: Propose one targeted change

Change only the suspected bottleneck.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **propose one targeted change** is qualified there.

## Exercise 6: Verify outside profiling

Rerun synchronized uninstrumented samples with equal outputs.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **verify outside profiling** is qualified there.

## Reference observation

Summed event durations 14 ms, complete interval 10 ms.

The reference file is `courses/cuda/python/references/cuda-092_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
