# r-025: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

values <- c(2, 4)
unit <- "ms"
plot_data <- data.frame(time = c(1, 2, 3), latency = c(4, 7, 9))

# Exercise 1: Predict the record summary for values c(2,4) and unitms.
# TODO: Retain count and unit alongside the mean.
# Exercise 2: Write an R6 adapter using public values() and unit() methods.
# TODO: Do not read private environments.
# Exercise 3: Write an S7 adapter using its declared properties.
# TODO: @ notation alone does not select the correct object system.
# Exercise 4: Diagnose unclass on an object whose numbers are seconds while callers assume milliseconds.
# TODO: A representation change is not a unit conversion.
# Exercise 5: Change the plotted latency values and inspect the built y coordinates.
# TODO: Test ggplot_build output rather than an internal object layout.
# Exercise 6: Test an empty record and explain why its mean is missing.
# TODO: Count zero supplies no observed average.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
