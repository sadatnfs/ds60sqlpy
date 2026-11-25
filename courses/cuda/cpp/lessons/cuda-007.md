# cuda-007: learner worksheet

Use this saved worksheet on any classroom platform. Optional CPU and NVIDIA observations have separate evidence labels. Do not claim a GPU run from a CPU model.

## Exercise 1

Reconstruct worked example 1 on paper before running its CPU reference. Multiply one million elements by 12 bytes, giving 12 MB, and divide by 600e9 bytes per second.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 2

Rework worked example 2 without copying its conclusion. Compute min(10 TFLOP/s, intensity times 500 GB/s) separately for intensity 2 and intensity 40.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 3

Estimate useful bytes for adding two length-1,000 float64 vectors.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 4

A calculation divides bytes by TFLOP/s and calls the result seconds. Diagnose it.

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 5

Why is a roofline less useful for a one-element kernel?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:

## Exercise 6

A tiled kernel reduces global reads but doubles register use. What evidence decides?

My prediction or design:

My calculation, trace or observation:

Evidence surface (reading / CPU reference / actual NVIDIA execution):

What this does not establish:
