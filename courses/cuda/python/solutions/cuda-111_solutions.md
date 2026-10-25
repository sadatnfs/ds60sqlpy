# cuda-111: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate arithmetic intensity

Divide operations by bytes.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate arithmetic intensity** is qualified there.

## Exercise 2: Count eliminated bytes

Count both avoided write and read.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count eliminated bytes** is qualified there.

## Exercise 3: Name a profiler counter

Choose a relevant measured traffic or stall metric.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **name a profiler counter** is qualified there.

## Exercise 4: Design one controlled change

Keep all other settings fixed.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design one controlled change** is qualified there.

## Exercise 5: Test a boundary shape

Use a nonmultiple and a tiny case.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **test a boundary shape** is qualified there.

## Exercise 6: Explain a failed optimization

Relate observed resource use and timing to the rejected hypothesis.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain a failed optimization** is qualified there.

## Reference observation

Intensity 0.5 and hypothetical 8192 bytes removable traffic.

The reference file is `courses/cuda/python/references/cuda-111_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
