# r-030: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

ids <- c("a", "b", "c")
values <- c(2, NA_real_, 6)
unit <- "ms"
results <- vector("list", 6L)

# Exercise 1: Predict the summary of values c(2,NA,6) with three unique IDs.
# TODO: Keep the row count separate from the observed denominator.
# Exercise 2: Add one new eight-millisecond record and recompute the summary.
# TODO: Use a new unique ID and the same unit.
# Exercise 3: Independently implement and test the duplicate-ID and equal-length constructor rules.
# TODO: Reject before creating a class-labeled value.
# Exercise 4: Diagnose returning zero for an all-missing batch.
# TODO: No observed measurement supports that mean.
# Exercise 5: Test a forged class object and incompatible-unit combination.
# TODO: Public operations validate again and avoid implicit conversion.
# Exercise 6: Write the package interface and state the inferential limit of a passing reference.
# TODO: Separate NAMESPACE registration, project workflow and statistical assumptions.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
