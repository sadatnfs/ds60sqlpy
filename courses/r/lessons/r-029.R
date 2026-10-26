# r-029: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

config <- list(seed = 2026L, draws = 5L, missing_policy = "reject")
fixture <- list(id = c("a", "b", "c"), value = c(2, 4, 6), unit = "ms")

# Exercise 1: Predict whether two with_rng calls with seed 2026 and identical callbacks match.
# TODO: The wrapper fixes both seed and generator kinds.
# Exercise 2: Test cleanup after a callback raises an error.
# TODO: Capture kind and seed before invoking the wrapper.
# Exercise 3: Test the case where .Random.seed did not exist before the call.
# TODO: A restoration policy includes absence.
# Exercise 4: Change one fixture value and compare its content digest.
# TODO: Hash the same explicit JSON representation rules.
# Exercise 5: Record only the configuration and software metadata needed to reproduce this calculation.
# TODO: Avoid whole-environment dumps.
# Exercise 6: Explain why a repeated result is not evidence that the estimator is unbiased.
# TODO: Numerical reproducibility and statistical assumptions are different.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
