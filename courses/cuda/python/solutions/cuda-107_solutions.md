# cuda-107: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Trace stable sorting

Equal-key records preserve input order.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace stable sorting** is qualified there.

## Exercise 2: Specify duplicate semantics

State whether order is guaranteed.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify duplicate semantics** is qualified there.

## Exercise 3: Calculate output shape

Outer dimensions become output.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate output shape** is qualified there.

## Exercise 4: Account for temporary storage

Workspace can affect peak live memory.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **account for temporary storage** is qualified there.

## Exercise 5: Separate plan creation

Measure cold setup and steady execution.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **separate plan creation** is qualified there.

## Exercise 6: Choose a release-specific contract

Use the documentation matching the prepared package.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **choose a release-specific contract** is qualified there.

## Reference observation

Stable duplicate order and matrix output shape (2,4).

The reference file is `courses/cuda/python/references/cuda-107_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
