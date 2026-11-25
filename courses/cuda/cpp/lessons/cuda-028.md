# cuda-028: learner worksheet

Use this saved worksheet on any classroom platform. Optional CPU and NVIDIA observations have separate evidence labels. Do not claim a GPU run from a CPU model.

## Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Order four events: write payload 42, release the ready flag, acquire the flag in the consumer, then read the payload.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 2

Rework worked example 2 without copying its conclusion. Separate the atomic counter from the payload protocol and add release and acquire to the publication.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 3

Name the four events in the publication chain.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 4

Why does a memory fence not make a sleeping producer execute?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 5

When might block-scope synchronization be insufficient?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 6

Apply the reasoning to a ring buffer slot.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:
