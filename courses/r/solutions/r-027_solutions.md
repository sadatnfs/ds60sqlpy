# r-027: reference reasoning

Use the [complete reference](r-027_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The independent small matrix supplies known row means, while the larger fixture compares the two implementations within numerical tolerance. The missing-value counterexample shows how a superficially faster implementation can answer a different question.

The reference retains timing and profiler observations without testing an environment-dependent speed ratio. Cleanup belongs to the profiling function, and object.size is labeled as an object estimate. These checks establish equivalent outputs and bounded measurement behavior, not a universal optimization ranking.

## Explained practice

### Exercise 1

Predict the row means of matrix(1:6,nrow=2).

The rows are 1,3,5 and 2,4,6, giving means 3 and 4.

**Expected evidence:** Means 3,4.

### Exercise 2

Replace repeated vector growth with a preallocated result.

Assign each mean into its existing result index; compare against rowMeans on the same input.

**Expected evidence:** Equal values without repeated c growth.

### Exercise 3

Measure both implementations with the same fixture and repetitions.

Report observed elapsed seconds for both; do not assert a fixed ratio or exact duration.

**Expected evidence:** Comparable measurement conditions.

### Exercise 4

Diagnose a faster version that silently removes missing observations.

It changes the computation. Decide one missingness policy first, then compare equivalent implementations.

**Expected evidence:** Correctness is checked before timing.

### Exercise 5

Collect a short Rprof and report a possible empty sample set honestly.

Report sampling.time and available entries, or explicitly state that the workload produced insufficient samples. Do not infer zero cost.

**Expected evidence:** Bounded profile with measurement limits.

### Exercise 6

Explain why object.size(x) cannot establish peak process memory.

It estimates the R object size, excluding a complete process/peak/shared-memory accounting. Use an appropriate process measurement for that separate question.

**Expected evidence:** No peak-memory overclaim.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
