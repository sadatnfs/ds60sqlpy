# r-060: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(id = c(paste0("A", 1:5), paste0("B", 1:5)), group = rep(c("A", "B"), each = 5), value = c(1, 2, 3, 4, NA_real_, 2, 3, 6, 7, NA_real_))
results <- vector("list", 6L)

# Exercise 1: Build the eligibility ledger from the ten raw records.
# TODO: Keep missing counts instead of silently dropping them.
# Exercise 2: Derive means, SEs and t-interval endpoints.
# TODO: Use the admitted raw values and df 3 for each group.
# Exercise 3: Construct a static raw-point and interval display from those tables.
# TODO: Use separate layer data and explicit inheritance.
# Exercise 4: Construct an interactive figure retaining raw IDs and a separate summary trace.
# TODO: Do not count summary marks as new observations.
# Exercise 5: Diagnose interpreting the mean difference as a causal effect.
# TODO: Identify the absent assignment/identification design.
# Exercise 6: Produce a factual report of what execution and capture established.
# TODO: Separate numeric, payload and browser evidence.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
