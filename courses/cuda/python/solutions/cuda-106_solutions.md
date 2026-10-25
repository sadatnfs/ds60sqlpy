# cuda-106: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Create tile boundaries

Use half-open intervals.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **create tile boundaries** is qualified there.

## Exercise 2: Mask a final tile

Guard both input and output.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **mask a final tile** is qualified there.

## Exercise 3: Compare thread and tile abstractions

The compiler owns more mapping decisions in a tile DSL.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare thread and tile abstractions** is qualified there.

## Exercise 4: State compiler requirements

Record exact release and supported architecture.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **state compiler requirements** is qualified there.

## Exercise 5: Design a library comparison

Match data shape dtype and timing boundary.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a library comparison** is qualified there.

## Exercise 6: Explain a resource tradeoff

Larger tiles can increase live state and reduce concurrency.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain a resource tradeoff** is qualified there.

## Reference observation

Three tiles cover ten elements exactly once.

The reference file is `courses/cuda/python/references/cuda-106_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
