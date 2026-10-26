# r-044: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(x = c(0, 1), successes = c(2, 6), failures = c(8, 4))
results <- vector("list", 6L)

# Exercise 1: Fit the two-group binomial model and reconstruct probabilities from the link scale.
# TODO: Use plogis on link predictions.
# Exercise 2: Interpret the x coefficient as an odds ratio.
# TODO: Calculate odds p/(1-p) at both x values.
# Exercise 3: Calculate the trial-weighted Brier score.
# TODO: Count successes and failures separately.
# Exercise 4: Diagnose treating the proportions 0.2 and 0.6 as two equally weighted binary observations.
# TODO: Retain the ten-trial denominator in each group.
# Exercise 5: Recognize complete separation for x=c(-2,-1,1,2) and y=c(0,0,1,1).
# TODO: Find a threshold that perfectly separates the labels.
# Exercise 6: Assess held-out group outcomes 1/10 and 8/10 under predictions 0.2 and 0.6.
# TODO: Compare probabilities with new frequencies, not the training groups.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
