# cuda-068: explained solutions

These answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.

## Exercise 1: Compute centered columns

The means are two and five.

**Approach.** Compute each column mean over the two rows, then subtract it: column 0 is `(1+3)/2 = 2`, column 1 is `(3+7)/2 = 5`, giving centered rows `[[-1,-2],[1,2]]`.

**Why it is correct here.** Centering subtracts the same per-column value from every row, which is a broadcast of a length-2 vector over a 2 by 2 array. Each centered column then sums to zero, a property the reference result satisfies.

**A plausible wrong approach.** Subtracting row means instead is tempting because they are also 2 and 5 here, a coincidence of this data. Broadcasting them down the wrong axis gives `[[-1,1],[-2,2]]`; the shapes still match, so no error appears, and the columns no longer sum to zero.

**How to verify.** Run the cuda-068 reference: it asserts `centered == [[-1.0, -2.0], [1.0, 2.0]]`. With CuPy or NumPy, `x - x.mean(axis=0)` must match, and `centered.sum(axis=0)` must be zeros.

## Exercise 2: Add a constant feature

A constant feature centers to zero.

**Approach.** Append a column of a constant, for example 5, to both rows. Its mean is 5, so after centering that column is all zeros.

**Why it is correct here.** Subtracting a column's mean from identical values always gives zero. On the GPU this is still exact for small integers stored as float32, so the result is a column of exact zeros.

**A plausible wrong approach.** Dividing by the column standard deviation after centering, as in standardization, divides zero by zero for this column and produces NaN that spreads into later steps.

**How to verify.** Extend the reference rows to `[[1,3,5],[3,7,5]]` and confirm the third centered column is `[0.0, 0.0]`. If you also scale, assert that the policy for zero variance is explicit, such as leaving the column at zero.

## Exercise 3: Implement distance directly

Sum squared coordinate differences.

**Approach.** Subtract coordinates first and then square and sum: `(1-4)**2 + (2-6)**2 = 9 + 16 = 25`.

**Why it is correct here.** The direct form never forms large squares of the original values, so it has no cancellation. For the integers in this example it is exact, matching the reference assertion `distance == 25`.

**A plausible wrong approach.** Taking a square root and reporting 5 answers a different question. The chapter defines squared distance, and mixing the two breaks comparisons against the reference.

**How to verify.** Run the reference and check `distance == 25`. With an array library, `((x - y) ** 2).sum()` on float32 inputs `[1,2]` and `[4,6]` must also give exactly 25.

## Exercise 4: Explain expanded-form cancellation

Subtracting nearly equal large terms loses significant digits.

**Approach.** Expand `|x-y|^2` as `|x|^2 + |y|^2 - 2 x.y` and construct inputs where the two first terms are large and nearly equal to the cross term, for example coordinates near `1e4` that differ by 1 in float32.

**Why it is correct here.** For `[1,2]` and `[4,6]` the expanded form gives `5 + 52 - 2*16 = 25` exactly. With large nearly equal vectors, float32 keeps about seven significant digits, so `|x|^2` around `1e8` cannot represent a difference of a few units and the subtraction loses the answer.

**A plausible wrong approach.** Concluding that the expanded form is safe because the small worked example matches is the trap. Exact agreement on tiny integers says nothing about inputs where the squared norms dominate.

**How to verify.** Compare the two forms in float32 and float64 on `x = [10000.0, 10000.0]`, `y = [10001.0, 10000.0]`. The direct form gives 1; check whether the float32 expanded form differs, and record the result as a CPU numeric observation.

## Exercise 5: Count a pairwise temporary

N by M by D elements can dominate memory.

**Approach.** Count the elements of the broadcast temporary `x[:, None, :] - y[None, :, :]`: it has shape `(N, M, D)`, so its size is `N*M*D` elements times itemsize.

**Why it is correct here.** Pairwise distance on N rows against M rows by broadcasting materializes every coordinate difference before the reduction over D. For N = M = 10000 and D = 64 in float32 that is 25.6 GB, far above the size of the final `(N, M)` result.

**A plausible wrong approach.** Counting only the output `N*M` elements underestimates peak memory by a factor of D. The allocation fails or swaps even though the result itself would fit.

**How to verify.** Compute `N*M*D*4` bytes for your chosen sizes and compare with device memory. A safe experiment checks the broadcast shape with tiny N and M first, for example `(2, 2, 2)` on the reference vectors.

## Exercise 6: Choose a library baseline

Use supported array operations before owning a kernel.

**Approach.** Write the baseline with supported array operations, such as `x.mean(axis=0)` and broadcast subtraction, before writing any custom kernel, and keep it as the oracle.

**Why it is correct here.** CuPy and NumPy implement these operations with tested dtype promotion and edge handling. The centering and distance in this chapter are a few library calls, so a custom kernel would have to beat a correct baseline rather than replace a missing one.

**A plausible wrong approach.** Starting with a raw kernel for centering means writing reduction, broadcasting and tail handling by hand, with no reference to tell whether a wrong column mean is a kernel bug or a math bug.

**How to verify.** Keep the library result for `[[1,3],[3,7]]` and the distance 25 as fixed test cases. Any later kernel must reproduce `[[-1,-2],[1,2]]` and 25 under a stated tolerance before its speed is discussed.

## Reference observation

Centered columns and distance 25.

The reference file is `courses/cuda/python/references/cuda-068_cpu.py`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.
