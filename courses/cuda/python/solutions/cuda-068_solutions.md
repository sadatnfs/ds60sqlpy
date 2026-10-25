# cuda-068: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute centered columns

The means are two and five.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute centered columns** is qualified there.

## Exercise 2: Add a constant feature

A constant feature centers to zero.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **add a constant feature** is qualified there.

## Exercise 3: Implement distance directly

Sum squared coordinate differences.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **implement distance directly** is qualified there.

## Exercise 4: Explain expanded-form cancellation

Subtracting nearly equal large terms loses significant digits.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain expanded-form cancellation** is qualified there.

## Exercise 5: Count a pairwise temporary

N by M by D elements can dominate memory.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count a pairwise temporary** is qualified there.

## Exercise 6: Choose a library baseline

Use supported array operations before owning a kernel.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a library baseline** is qualified there.

## Reference observation

Centered columns and distance 25.

The reference file is `courses/cuda/python/references/cuda-068_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
