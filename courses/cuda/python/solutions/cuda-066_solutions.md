# cuda-066: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Calculate offset (1,1)

Offset is 16 bytes in the original matrix.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **calculate offset (1,1)** is qualified there.

## Exercise 2: Change dtype to float64

Element width and strides double.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **change dtype to float64** is qualified there.

## Exercise 3: Describe a transposed view

Transpose exchanges shape axes and strides.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **describe a transposed view** is qualified there.

## Exercise 4: Find the contiguous-only bug

Using row*width+col ignores actual strides.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **find the contiguous-only bug** is qualified there.

## Exercise 5: Specify negative-stride support

Reject or implement negative strides explicitly.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify negative-stride support** is qualified there.

## Exercise 6: Design layout contract tests

Include contiguous, sliced, transposed, empty and wrong dtype.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design layout contract tests** is qualified there.

## Reference observation

All three views address byte offset 20.

The reference file is `courses/cuda/python/references/cuda-066_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
