# r-028: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

tasks <- list(1:3, 4:6, c(2, 2))
worker_count <- 2L

# Exercise 1: Predict the squared sums for tasks 1:3 and 4:6.
# TODO: Compute the serial arithmetic first.
# Exercise 2: Add a third deterministic task c(2,2) without increasing the worker count.
# TODO: Worker count and task count are different.
# Exercise 3: Implement a self-contained task that returns count and squared sum.
# TODO: Return a named list instead of console text or shared-file writes.
# Exercise 4: Diagnose assigning the same set.seed value inside every simulation task.
# TODO: Deterministic can still mean wrongly identical simulations.
# Exercise 5: Compare static scheduling and reversed load-balanced scheduling.
# TODO: Carry stream state with each task and reorder results by identifier.
# Exercise 6: Explain cleanup for an ordinary R error versus a forced deadline.
# TODO: An R handler cannot run after every possible external kill.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
