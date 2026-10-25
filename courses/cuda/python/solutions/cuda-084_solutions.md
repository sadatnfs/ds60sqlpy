# cuda-084: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Derive expected affine output

Apply the formula elementwise.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **derive expected affine output** is qualified there.

## Exercise 2: Calculate a nonmultiple launch

Ceiling division gives three blocks.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate a nonmultiple launch** is qualified there.

## Exercise 3: Explain symbol lookup

The compiled exported name must match.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain symbol lookup** is qualified there.

## Exercise 4: Reject noncontiguous input or support strides

State one layout contract explicitly.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **reject noncontiguous input or support strides** is qualified there.

## Exercise 5: Separate compile timing

Warm the same code before steady-state samples.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate compile timing** is qualified there.

## Exercise 6: Compare raw and library paths

Compare outputs and complete work under the same tolerance.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **compare raw and library paths** is qualified there.

## Reference observation

Affine result [-1,1,7], with three blocks for 257 elements.

The reference file is `courses/cuda/python/references/cuda-084_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
