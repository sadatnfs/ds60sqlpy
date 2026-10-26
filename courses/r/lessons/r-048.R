# r-048: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(time = c(1, 2, 3, 4), event = c(1, 0, 1, 1))
results <- vector("list", 6L)

# Exercise 1: Reconstruct the four-record Kaplan-Meier steps.
# TODO: Update the risk set after the censor at time two.
# Exercise 2: Treat the censor at time two as an event and compare the resulting curve.
# TODO: Change only the event indicator.
# Exercise 3: Validate an event column before creating Surv.
# TODO: Require a declared binary coding rather than relying on guessing.
# Exercise 4: Fit the Cox fixture and convert its coefficient to a hazard ratio.
# TODO: Exponentiate the log-hazard coefficient.
# Exercise 5: Inspect cox.zph output without turning its p-value into proof of proportional hazards.
# TODO: Identify the diagnostic and its sampling limits.
# Exercise 6: Explain why averaging observed event times after dropping censored rows changes the analysis.
# TODO: Ask which survival information was discarded.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
