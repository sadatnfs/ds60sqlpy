# r-043: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(x = 0:4, y = c(1, 3, 4, 7, 8))
results <- vector("list", 6L)

# Exercise 1: Recover the design matrix for y~x on the five-row fixture.
# TODO: Inspect the intercept column.
# Exercise 2: Predict at x=5 and label its support relative to training.
# TODO: The training x values end at 4.
# Exercise 3: Fit y~x*group to two exact group lines A:1+2x and B:4+x.
# TODO: Expand the interaction columns and use A as reference.
# Exercise 4: Add double_x=2*x and diagnose y~x+double_x.
# TODO: Compare QR rank with design column count.
# Exercise 5: Check residual orthogonality for the simple fit.
# TODO: Multiply X-transpose by the residual vector.
# Exercise 6: Explain why the prediction interval is wider than the mean confidence interval.
# TODO: Name the additional random quantity.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
