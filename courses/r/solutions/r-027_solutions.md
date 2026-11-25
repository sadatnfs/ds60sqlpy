# r-027: reference reasoning

Run the [complete reference](r-027_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The independent small matrix supplies known row means, while the larger fixture compares the two implementations within numerical tolerance. The missing-value counterexample shows how a superficially faster implementation can answer a different question.

The reference retains timing and profiler observations without testing an environment-dependent speed ratio. Cleanup belongs to the profiling function, and object.size is labeled as an object estimate. These checks establish equivalent outputs and bounded measurement behavior, not a universal optimization ranking.

## Explained practice

### Exercise 1

Predict the row means of matrix(1:6,nrow=2).

The rows are 1,3,5 and 2,4,6, giving means 3 and 4.

**Expected evidence:** Means 3,4.

**Approach:** Write out the matrix before averaging: `matrix(1:6, nrow = 2)` fills column by column, so the columns are 1 and 2, 3 and 4, 5 and 6.

**Why it holds here:** Row 1 therefore holds 1, 3 and 5 with mean 3, and row 2 holds 2, 4 and 6 with mean 4. Both the loop and rowMeans read the same rows.

**Tempting mistake:** Assuming rows are filled first. That layout gives rows 1, 2, 3 and 4, 5, 6 with means 2 and 5, which requires `byrow = TRUE` and is not what this call builds.

**Verify:** `identical(row_means_loop(small), c(3, 4))` returns TRUE, and `small[1, ]` shows 1, 3, 5.

### Exercise 2

Replace repeated vector growth with a preallocated result.

Assign each mean into its existing result index; compare against rowMeans on the same input.

**Expected evidence:** Equal values without repeated c growth.

**Approach:** Allocate `result <- numeric(nrow(x))` before the loop, assign `result[[i]]` inside it, and compare the output with rowMeans on the same matrix.

**Why it holds here:** For the 300 row fixture, growing with c() copies the whole output each time, about 45 thousand element copies in total. Preallocation writes each of the 300 slots once, and the means are identical because each is computed the same way.

**Tempting mistake:** Keeping `output <- c(output, mean(x[i, ]))`. The values are right, so nothing fails, but the copying grows with the square of the row count and dominates on larger inputs.

**Verify:** `isTRUE(all.equal(growing(x), row_means_loop(x)))` returns TRUE, and `length(row_means_loop(x))` returns 300.

### Exercise 3

Measure both implementations with the same fixture and repetitions.

Report observed elapsed seconds for both; do not assert a fixed ratio or exact duration.

**Expected evidence:** Comparable measurement conditions.

**Approach:** Build x once outside the timers, wrap only the repeated calls in `system.time()` with the same 20 repetitions for both versions, and report both elapsed values with that count.

**Why it holds here:** Both timings use the same 300 by 20 matrix after all.equal has confirmed equal results, so the numbers describe the same work. Elapsed time depends on the machine and its load, which is why the reference checks only that each is nonnegative.

**Tempting mistake:** Asserting a fixed ratio such as ten times faster, or creating the matrix inside one timer. The ratio fails on a busy runner, and setup inside one timer charges that version for extra work.

**Verify:** `result$loop_seconds` and `result$vector_seconds` both return nonnegative numbers, reported together with the 20 repetitions.

### Exercise 4

Diagnose a faster version that silently removes missing observations.

It changes the computation. Decide one missingness policy first, then compare equivalent implementations.

**Expected evidence:** Correctness is checked before timing.

**Approach:** Choose the missingness policy first, then compare only implementations that follow it.

**Why it holds here:** In `matrix(c(1, NA_real_, 3, 4), nrow = 2)` the second row holds NA and 4. rowMeans propagates the NA, while `na.rm = TRUE` returns 4, so the two versions compute different answers and timing them against each other compares two different tasks.

**Tempting mistake:** Accepting the na.rm version because it is faster and its output has no gaps. It reports 4 for a row with a missing observation, and only a fixture containing NA reveals the change.

**Verify:** `rowMeans(missing)[[2]]` returns NA, while `rowMeans(missing, na.rm = TRUE)[[2]]` returns 4.

### Exercise 5

Collect a short Rprof and report a possible empty sample set honestly.

Report sampling.time and available entries, or explicitly state that the workload produced insufficient samples. Do not infer zero cost.

**Expected evidence:** Bounded profile with measurement limits.

**Approach:** Profile 30 runs of the loop with `Rprof(path, interval = 0.01)`, stop it with `Rprof(NULL)`, summarize, and report sampling.time with the top entries, or say plainly that no samples were taken.

**Why it holds here:** Rprof records the call stack every 10 milliseconds. If the 30 runs over 300 rows finish quickly, few or no samples land, so by.total can be empty; the reference allows a sampled time of 0.

**Tempting mistake:** Reading an empty profile as proof that the loop costs nothing, or forgetting to stop profiling. The reference also registers `on.exit(utils::Rprof(NULL))` so an error cannot leave it running.

**Verify:** `result$sampled_seconds` returns the sampled time, possibly 0, and `nrow(result$top)` shows how many functions were sampled.

### Exercise 6

Explain why object.size(x) cannot establish peak process memory.

It estimates the R object size, excluding a complete process/peak/shared-memory accounting. Use an appropriate process measurement for that separate question.

**Expected evidence:** No peak-memory overclaim.

**Approach:** Report `object.size(x)` as the size of the input matrix only, and use a process level measurement for peak memory.

**Why it holds here:** x holds 6000 doubles at 8 bytes each, so its size is a little above 48 thousand bytes. The loop also allocates a temporary row with `x[i, ]` on every pass, and none of those temporaries appear in object.size(x).

**Tempting mistake:** Stating that the computation peaks at about 48 kilobytes. The growing version creates up to 300 intermediate vectors, and how many are alive at once depends on when garbage collection runs.

**Verify:** `result$input_bytes` returns a value a little above 48000 and stays the same whichever implementation runs.

## What the checks establish

The checks confirm finite numeric input, agreement between the loop and vectorized versions within 1e-12, row means of 3 and 4 for the small matrix, equal results from the growing and preallocated loops and `rowMeans()`, NA propagation unless `na.rm = TRUE`, and nonnegative timing and profile fields. They deliberately do not assert which version is faster, because timings vary between runs and machines.

The reference makes 8 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
