# cuda-119: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute resource-share slots

One divided by 0.25 gives four accounting slots.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute resource-share slots** is qualified there.

## Exercise 2: Compare CPU and GPU limits

The effective bound includes all constraints.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare CPU and GPU limits** is qualified there.

## Exercise 3: Explain VRAM nonpartitioning

Scheduling fractions do not reserve fixed memory slices.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain VRAM nonpartitioning** is qualified there.

## Exercise 4: Verify device addresses

Inspect explicit discovery and assignment.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **verify device addresses** is qualified there.

## Exercise 5: Design a concurrency experiment

Hold query partitions and data fixed.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a concurrency experiment** is qualified there.

## Exercise 6: Describe oversubscription failure

Too many live tasks can spill or fail without any syntax error.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **describe oversubscription failure** is qualified there.

## Reference observation

Four scheduling shares with a two-task plugin admission bound.

The reference file is `courses/cuda/spark/references/cuda-119_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
