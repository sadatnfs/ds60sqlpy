# cuda-076: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Choose a sum identity

Use zero.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a sum identity** is qualified there.

## Exercise 2: Choose a minimum identity

Use a sentinel outside the valid domain or carry validity.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a minimum identity** is qualified there.

## Exercise 3: Trace barrier participants

All block lanes reach the barrier.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace barrier participants** is qualified there.

## Exercise 4: Repair early return

Guard data access instead of participation.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **repair early return** is qualified there.

## Exercise 5: Separate block and grid scope

Shared memory is per block.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate block and grid scope** is qualified there.

## Exercise 6: Design a nonmultiple test

Use n=blocksize+1 with explicit expected output.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design a nonmultiple test** is qualified there.

## Reference observation

All four modeled lanes participate; padded sum is 12.

The reference file is `courses/cuda/python/references/cuda-076_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
