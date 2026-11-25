# cuda-014: learner worksheet

Use this saved worksheet on any classroom platform. Optional CPU and NVIDIA observations have separate evidence labels. Do not claim a GPU run from a CPU model.

## Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Set stride to the total thread count 2 * 4 = 8 and list i, i + 8, i + 16 below 19 for each thread.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 2

Rework worked example 2 without copying its conclusion. Add [0, 1, 2, 3, 4] and [5, 4, 3, 2, 1], then repeat with 33 distinct values and empty and singleton inputs.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 3

Give the indices owned by starting thread 5 when \(\mathrm{stride}=8\) and \(\mathrm{n}=22\).

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 4

A kernel tests `i <= n` instead of `i < n`. Diagnose it.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 5

How many blocks are required for \(\mathrm{n}=33\) with 32 threads under one-element mapping?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 6

Transfer the proof to a streaming chunk with a global offset.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:
