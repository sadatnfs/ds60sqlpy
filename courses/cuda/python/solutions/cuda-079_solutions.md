# cuda-079: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Count touched segments

Count distinct integer offsets divided by segment size.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count touched segments** is qualified there.

## Exercise 2: Shift the base by four bytes

The shift may cross a boundary.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **shift the base by four bytes** is qualified there.

## Exercise 3: Model a stride of two

Stride can increase transaction count.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **model a stride of two** is qualified there.

## Exercise 4: Explain tiled transpose

Shared storage rearranges cooperative ownership.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain tiled transpose** is qualified there.

## Exercise 5: Separate occupancy from throughput

More resident work can still compete for resources.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate occupancy from throughput** is qualified there.

## Exercise 6: Propose a matched profiler experiment

Hold dtype shape and output fixed and inspect real counters.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **propose a matched profiler experiment** is qualified there.

## Reference observation

Simplified segment counts 1 and 8, not hardware measurements.

The reference file is `courses/cuda/python/references/cuda-079_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
