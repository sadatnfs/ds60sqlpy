# cuda-074: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute launch size for n=17

Five blocks of four are enough.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compute launch size for n=17** is qualified there.

## Exercise 2: Trace the last block

Indices 17..19 are out of range.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace the last block** is qualified there.

## Exercise 3: Test zero without launching

Return empty before launch.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **test zero without launching** is qualified there.

## Exercise 4: Implement grid-stride coverage

Advance by grid size times block size.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **implement grid-stride coverage** is qualified there.

## Exercise 5: Find floor-division data loss

Floor division omits the final partial block.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **find floor-division data loss** is qualified there.

## Exercise 6: Specify a sanitizer check

Run real kernels under supported memory checking separately.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify a sanitizer check** is qualified there.

## Reference observation

Every valid index appears exactly once.

The reference file is `courses/cuda/python/references/cuda-074_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
