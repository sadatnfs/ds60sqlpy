# r-027: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

small <- matrix(1:6, nrow = 2)
workload <- matrix(seq_len(6000) / 100, nrow = 300)

# Exercise 1: Predict the row means of matrix(1:6,nrow=2).
# TODO: R fills the matrix by columns.
# Exercise 2: Replace repeated vector growth with a preallocated result.
# TODO: Allocate numeric(nrow(x)) before the loop.
# Exercise 3: Measure both implementations with the same fixture and repetitions.
# TODO: Exclude input creation and retain the repeat count.
# Exercise 4: Diagnose a faster version that silently removes missing observations.
# TODO: The original operation propagates missingness unless specified otherwise.
# Exercise 5: Collect a short Rprof and report a possible empty sample set honestly.
# TODO: Sampling can miss brief work.
# Exercise 6: Explain why object.size(x) cannot establish peak process memory.
# TODO: Object accounting and whole-process usage differ.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
