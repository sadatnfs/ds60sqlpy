# cuda-072: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Order the evidence levels

Import, visibility, allocation, launch, completion and correctness.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **order the evidence levels** is qualified there.

## Exercise 2: Classify missing device

Inspect explicit runtime exposure and host capability.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **classify missing device** is qualified there.

## Exercise 3: Classify wrong output

Correctness failure after execution.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **classify wrong output** is qualified there.

## Exercise 4: Design fail-closed device selection

Require requested backend and visible device.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design fail-closed device selection** is qualified there.

## Exercise 5: Explain process restart after fatal device error

Discard unhealthy execution context.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain process restart after fatal device error** is qualified there.

## Exercise 6: Compare alternative backend labels

Name CUDA, ROCm, MPS or CPU truthfully.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare alternative backend labels** is qualified there.

## Reference observation

Fixture fails at correctness, not readiness success.

The reference file is `courses/cuda/python/references/cuda-072_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
