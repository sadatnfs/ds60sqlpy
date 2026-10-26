# r-022: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

values <- c(1, 3)
second_values <- 5
unit <- "ms"

# Exercise 1: Predict the result of combining c(1,3)ms with5ms.
# TODO: The operation concatenates observations.
# Exercise 2: Change the second input to seconds and test the failure.
# TODO: The signature still matches; values within the slots differ.
# Exercise 3: Construct a new object with an infinite measurement.
# TODO: The numeric type alone is insufficient.
# Exercise 4: Diagnose a direct x@unit <- character(0) assignment.
# TODO: It is character but not one nonempty string.
# Exercise 5: Test the FormalMeasure,numeric method separately.
# TODO: An unlabeled numeric vector cannot establish units.
# Exercise 6: Design a safe seconds-to-milliseconds conversion boundary.
# TODO: Conversion changes both values and unit.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
