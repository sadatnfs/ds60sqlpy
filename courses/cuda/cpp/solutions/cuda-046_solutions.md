# cuda-046: explanatory solutions

## Mechanism review

GEMM computes scaled matrix multiplication plus an existing output contribution. In conventional notation, C becomes alpha times A*B plus beta times C. Classic cuBLAS uses column-major conventions, so leading dimensions and transpose flags must be interpreted accordingly. cuBLASLt provides more explicit layout and algorithm descriptors, with workspace and compute-type choices. A handle has lifecycle and stream configuration. Check library status separately from CUDA completion. A successful call with wrong dimensions can produce plausible but incorrect data, especially when symmetric inputs conceal transposition mistakes.

## Exercise 1

Use the rectangular A and B from cuda-018, whose product is \([[7,4],[16,13]]\). With \(\alpha=2\), \(\beta=3\) and initial C all ones, the result becomes \([[17,11],[35,29]]\). This catches implementations that ignore beta or assume the output is initially zero.

**Approach:** Compute alpha times A times B plus beta times C with alpha 2, beta 3 and C initialized to ones.

**Why it is correct:** The product [[7, 4], [16, 13]] doubles to [[14, 8], [32, 26]], and adding 3 to every entry gives [[17, 11], [35, 29]].

**A plausible wrong approach:** Ignoring beta returns [[14, 8], [32, 26]], and assuming C starts at zero hides that mistake on a fresh buffer.

**How to verify:** The reference asserts result == [[17, 11], [35, 29]]; on a GPU initialize C to ones explicitly before the call.

## Exercise 2

For column-major storage, a 2-by-3 matrix \([[1,2,3],[4,5,6]]\) is flattened \([1,4,2,5,3,6]\), with leading dimension two. Row-major flattening is \([1,2,3,4,5,6]\). Passing one while describing the other changes the interpretation rather than merely the speed.

**Approach:** Flatten the 2-by-3 matrix by columns to [1, 4, 2, 5, 3, 6] with leading dimension 2.

**Why it is correct:** Column-major order stores each column contiguously, so the leading dimension equals the row count.

**A plausible wrong approach:** Passing the row-major buffer [1, 2, 3, 4, 5, 6] while declaring column-major makes the library read a different 2-by-3 matrix with no error.

**How to verify:** The reference asserts column_major == [1, 4, 2, 5, 3, 6]; compare a cuBLAS result against the host product for this matrix.

## Exercise 3

\([[2,6],[4,8]]\), subject to the selected API's documented requirements for unused operands.

**Approach:** Set the product term to zero with alpha 0 and scale C = [[1, 3], [2, 4]] by beta 2.

**Why it is correct:** Only 2 times C remains, giving [[2, 6], [4, 8]], independent of what A and B hold.

**A plausible wrong approach:** Skipping the call entirely when alpha is zero leaves C unscaled at [[1, 3], [2, 4]].

**How to verify:** Run the call with arbitrary A and B and assert C becomes [[2, 6], [4, 8]].

## Exercise 4

It can hide a layout mismatch on symmetric shapes. Derive offsets and test rectangular distinct-valued matrices.

**Approach:** Derive leading dimensions and transpose flags from the stored layout, then test rectangular distinct values.

**Why it is correct:** A rectangular case with unique entries changes output if any offset is wrong.

**A plausible wrong approach:** Swapping m, n or transpose flags until a square test passes can leave the layout wrong in every other shape.

**How to verify:** Use a 3-by-5 times 5-by-2 fixture with distinct values and compare every element.

## Exercise 5

The old C values do not contribute; still follow the library's actual pointer and allocation requirements.

**Approach:** Treat beta 0 as old C contributing nothing, while still passing a valid C pointer.

**Why it is correct:** Mathematically the result is alpha times A times B regardless of the old C.

**A plausible wrong approach:** Leaving C uninitialized and assuming that is fine without checking the library contract may propagate NaN in some implementations.

**How to verify:** Fill C with NaN, call with beta 0, and confirm the output contains no NaN.

## Exercise 6

Match shape, layout, dtype, accumulation and alpha/beta semantics, include setup/workspace costs as appropriate, and validate against an independent oracle.

**Approach:** Match shape, layout, dtype, accumulation and alpha and beta, and include setup and workspace as appropriate.

**Why it is correct:** Only identical semantics make a time difference meaningful.

**A plausible wrong approach:** Comparing a handwritten float kernel with a library double call compares different work.

**How to verify:** Validate both outputs against an independent oracle before comparing repeated timings.

## Self-check answers

1. **What is the leading dimension of a column-major 3-by-4 matrix without padding?** 3, the number of rows.
2. **Why does worked example 1 use beta equal to 3 with C initialized to ones?** It catches code that ignores beta or assumes C starts at zero.
3. **What should beta equal to 0 mean?** The old C does not contribute, so even NaN values in C must not affect the result.

## Numerical reference and its limits

The [CPU reference](../references/cuda-046_cpu.py) reproduces worked example 1 and prints `{'scaled_GEMM': [[17, 11], [35, 29]], 'column_major': [1, 4, 2, 5, 3, 6]}`.

## Transfer review

Match shape, layout, dtype, accumulation and alpha/beta semantics, include setup/workspace costs as appropriate, and validate against an independent oracle.
