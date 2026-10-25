# cuda-075: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Trace a rectangular tile

List rows and columns independently.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **trace a rectangular tile** is qualified there.

## Exercise 2: Calculate flat offsets

Use `row * width + column`.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate flat offsets** is qualified there.

## Exercise 3: Change clamp to zero padding

State the changed edge semantics.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **change clamp to zero padding** is qualified there.

## Exercise 4: Find in-place stencil contamination

Earlier writes alter later reads.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **find in-place stencil contamination** is qualified there.

## Exercise 5: Test width one

Clamping repeats the only element.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **test width one** is qualified there.

## Exercise 6: Explain row and column tail guards

Both coordinates need their own upper bound.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain row and column tail guards** is qualified there.

## Reference observation

Clamped horizontal average [4, 6, 8].

The reference file is `courses/cuda/python/references/cuda-075_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
