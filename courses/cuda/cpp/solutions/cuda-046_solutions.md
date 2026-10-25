# cuda-046: explanatory solutions

## Mechanism review

GEMM computes scaled matrix multiplication plus an existing output contribution. In conventional notation, C becomes alpha times A*B plus beta times C. Classic cuBLAS uses column-major conventions, so leading dimensions and transpose flags must be interpreted accordingly. cuBLASLt provides more explicit layout and algorithm descriptors, with workspace and compute-type choices. A handle has lifecycle and stream configuration. Check library status separately from CUDA completion. A successful call with wrong dimensions can produce plausible but incorrect data, especially when symmetric inputs conceal transposition mistakes.

The separate [CPU reference](../references/cuda-046_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.

## Exercise 1

Use the rectangular A and B from cuda-018, whose product is \([[7,4],[16,13]]\). With \(\alpha=2\), \(\beta=3\) and initial C all ones, the result becomes \([[17,11],[35,29]]\). This catches implementations that ignore beta or assume the output is initially zero.

## Exercise 2

For column-major storage, a 2-by-3 matrix \([[1,2,3],[4,5,6]]\) is flattened \([1,4,2,5,3,6]\), with leading dimension two. Row-major flattening is \([1,2,3,4,5,6]\). Passing one while describing the other changes the interpretation rather than merely the speed.

## Exercise 3

\([[2,6],[4,8]]\), subject to the selected API's documented requirements for unused operands.

## Exercise 4

It can hide a layout mismatch on symmetric shapes. Derive offsets and test rectangular distinct-valued matrices.

## Exercise 5

The old C values do not contribute; still follow the library's actual pointer and allocation requirements.

## Exercise 6

Match shape, layout, dtype, accumulation and alpha/beta semantics, include setup/workspace costs as appropriate, and validate against an independent oracle.

## Numerical reference and its limits

The complete CPU model is [here](../references/cuda-046_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.

## Transfer review

Match shape, layout, dtype, accumulation and alpha/beta semantics, include setup/workspace costs as appropriate, and validate against an independent oracle.

A complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.
