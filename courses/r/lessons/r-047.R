# r-047: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(x = 1:8, label = factor(rep(c("low", "high"), each = 4), levels = c("low", "high")))
results <- vector("list", 6L)

# Exercise 1: Fit the declared depth-one classifier and predict x = 2 and x = 7.
# TODO: Retain explicit response levels and method.
# Exercise 2: Inspect the probability matrix and its column identities.
# TODO: Do not treat column position as an undocumented class label.
# Exercise 3: Prune with cp 1 and count terminal leaves.
# TODO: Inspect the returned object rather than the original fit.
# Exercise 4: Diagnose using perfect training accuracy to choose a complex tree.
# TODO: Separate fit from independent evaluation.
# Exercise 5: Implement a complete-finite-predictor admission policy for this application.
# TODO: Check new inputs before calling predict.
# Exercise 6: Predict at x = 1000 and explain the extrapolation limit.
# TODO: Follow the terminal region beyond the training maximum.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
