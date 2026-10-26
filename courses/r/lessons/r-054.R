# r-054: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(category = factor(c("A", "A", "B", "C", "C", "C"), levels = c("A", "B", "C")))
results <- vector("list", 6L)

# Exercise 1: Count six raw category records with geom_bar.
# TODO: Do not supply a precomputed y height to the count statistic.
# Exercise 2: Draw an existing count table with geom_col.
# TODO: Use its n column as the identity height.
# Exercise 3: Diagnose geom_bar(aes(category,n)) with the default statistic.
# TODO: Check the count statistic's input contract.
# Exercise 4: Construct two person-specific lines over shared times.
# TODO: Map group to person explicitly.
# Exercise 5: Build a histogram with explicit binwidth and boundary and verify total count.
# TODO: Inspect the post-statistic count column.
# Exercise 6: Explain why changing bins can change a visual conclusion without changing observations.
# TODO: Separate data from the layer transformation.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
