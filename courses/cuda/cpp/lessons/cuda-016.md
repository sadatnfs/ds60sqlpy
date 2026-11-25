# cuda-016: learner worksheet

Use this saved worksheet on any classroom platform. Optional CPU and NVIDIA observations have separate evidence labels. Do not claim a GPU run from a CPU model.

## Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Map each object to a space: images in global, sum in a register, tile in shared, taps in constant.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 2

Rework worked example 2 without copying its conclusion. Multiply 1,024 floats by 4 bytes, then by 128 threads.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 3

Assign storage for a reused image, a block tile and a scalar sum.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 4

An author says a local array is guaranteed to stay in registers. Correct the claim.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 5

Can one block read another block's ordinary shared array?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 6

Decide whether to use constant storage for a 64-entry lookup table.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:
