# r-045: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(id = 1:8, group = rep(LETTERS[1:4], each = 2), x = 0:7)
results <- vector("list", 6L)

# Exercise 1: Construct a group-disjoint split for four two-row families.
# TODO: Partition families before selecting their rows.
# Exercise 2: Demonstrate why an odd/even row split leaks the same families.
# TODO: Compare family sets as well as row IDs.
# Exercise 3: Perform leave-one-group-out prediction for the exact rule y=1+2x.
# TODO: Refit the model using only the other groups.
# Exercise 4: Diagnose centering with the full dataset before splitting.
# TODO: Ask which observations estimated the center.
# Exercise 5: Define the temporal split at day 4 in days 1 through 6.
# TODO: Keep every training date earlier than every assessment date.
# Exercise 6: Aggregate folds with error sums 2 and 12 and counts 1 and 3.
# TODO: Choose observation weighting explicitly.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
