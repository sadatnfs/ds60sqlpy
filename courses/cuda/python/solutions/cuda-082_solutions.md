# cuda-082: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Draw the dependency graph

Edges encode actual data dependencies.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **draw the dependency graph** is qualified there.

## Exercise 2: Locate a missing wait

Reading before the producing event is unsafe.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **locate a missing wait** is qualified there.

## Exercise 3: Separate host wait and stream wait

One blocks host progress and the other queues device ordering.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate host wait and stream wait** is qualified there.

## Exercise 4: Trace storage reuse

Do not recycle before final consumer completion.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace storage reuse** is qualified there.

## Exercise 5: Design non-default stream test

Use two streams and known values.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design non-default stream test** is qualified there.

## Exercise 6: Explain why global synchronization can mask bugs

Global waits accidentally add dependencies absent from the intended program.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain why global synchronization can mask bugs** is qualified there.

## Reference observation

Valid dependency order accepted; premature download rejected.

The reference file is `courses/cuda/python/references/cuda-082_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
