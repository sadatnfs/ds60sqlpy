# cuda-083: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Specify the kernel signature

Name pointer element types and scalar widths.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **specify the kernel signature** is qualified there.

## Exercise 2: Count allocation bytes

Elements times itemsize.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **count allocation bytes** is qualified there.

## Exercise 3: Classify compile versus launch errors

Compile checks source while launch tests executable compatibility.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **classify compile versus launch errors** is qualified there.

## Exercise 4: Design cleanup order

Wait for users then release resources.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **design cleanup order** is qualified there.

## Exercise 5: Explain ABI mismatch

Wrong byte interpretation can corrupt arguments.

Connect this conclusion to worked example 1 and the declared contract. State what additional observation would be needed on your actual backend before claiming **explain ABI mismatch** is qualified there.

## Exercise 6: Define release-pinned evidence

Record component versions target architecture and exact source.

Connect this conclusion to worked example 2 and the declared contract. State what additional observation would be needed on your actual backend before claiming **define release-pinned evidence** is qualified there.

## Reference observation

Insufficient storage for five float64 values is rejected.

The reference file is `courses/cuda/python/references/cuda-083_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
