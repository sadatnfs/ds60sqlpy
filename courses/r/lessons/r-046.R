# r-046: independent practice
# Supplied input fixture only; fill results and add independent assertions.

x <- cbind(short = c(-2, -1, 1, 2), long = c(-20, -10, 10, 20))
results <- vector("list", 6L)

# Exercise 1: Compare scaled and unscaled PCA for the proportional two-feature fixture.
# TODO: Separate feature units from information content.
# Exercise 2: Reconstruct a full two-component standardized fit.
# TODO: Undo the projection, scale and center in the correct order.
# Exercise 3: Reverse the first loading and score signs together.
# TODO: Compare the resulting reconstruction.
# Exercise 4: Diagnose a constant feature under scale.=TRUE.
# TODO: Inspect its standard deviation.
# Exercise 5: Transform a new row using predict and the saved center/scale/rotation.
# TODO: Do not refit PCA on the new row.
# Exercise 6: Explain why nearly 100% explained variance is not a downstream prediction-quality result.
# TODO: Ask whether the target participated in the objective.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
