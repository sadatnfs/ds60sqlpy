# cuda-069: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Predict repeated seeding

Repeated initialization repeats the sequence.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **predict repeated seeding** is qualified there.

## Exercise 2: Continue a stream

Retain the generator between batches.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **continue a stream** is qualified there.

## Exercise 3: Restore generator state

Save state before drawing.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **restore generator state** is qualified there.

## Exercise 4: Design a distribution check

Check sample mean and variance with tolerances.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a distribution check** is qualified there.

## Exercise 5: Separate backend equality from exact bytes

Use numeric or statistical contracts.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate backend equality from exact bytes** is qualified there.

## Exercise 6: List checkpoint randomness

Include Python, NumPy, framework, device and sampler state.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **list checkpoint randomness** is qualified there.

## Reference observation

Restored batch matches and continued batch differs.

The reference file is `courses/cuda/python/references/cuda-069_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
