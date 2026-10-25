# cuda-120: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute concurrent live memory

Add per-task live sets and shared state.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute concurrent live memory** is qualified there.

## Exercise 2: Lower concurrency

Reduce simultaneous live demand.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **lower concurrency** is qualified there.

## Exercise 3: Separate JVM and device pools

They are separate allocators and resources.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate JVM and device pools** is qualified there.

## Exercise 4: Budget spill disk

Use explicit disposable paths and capacity.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **budget spill disk** is qualified there.

## Exercise 5: Design safe batch changes

Bound rows and bytes before launch.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design safe batch changes** is qualified there.

## Exercise 6: Interpret successful but spilling execution

Completion is valid but performance and storage behavior need reporting.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **interpret successful but spilling execution** is qualified there.

## Reference observation

One through three tasks fit the simplified budget; four do not.

The reference file is `courses/cuda/spark/references/cuda-120_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
