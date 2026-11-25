# cuda-017: learner worksheet

Use this saved worksheet on any classroom platform. Optional CPU and NVIDIA observations have separate evidence labels. Do not claim a GPU run from a CPU model.

## Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Load [3, 6, 9, 12] into the tile, synchronize, then read tile[3 - t].

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 2

Rework worked example 2 without copying its conclusion. Load zero for lane three, have all four threads reach the barrier, store only valid lanes.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 3

Draw the producer and consumer for reversed output index zero.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 4

A conditional barrier hangs only on ragged input. What is the smallest repair?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 5

Why does a block barrier not make a global reduction complete?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 6

Design a neighbor-average tile with a halo.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:
