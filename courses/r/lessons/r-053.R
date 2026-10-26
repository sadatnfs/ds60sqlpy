# r-053: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(x = 1:4, y = c(1, 3, 2, 6), group = factor(c("A", "A", "B", "B"), levels = c("A", "B")))
results <- vector("list", 6L)

# Exercise 1: Map group to colour and shape for the four-row fixture.
# TODO: Place the variable inside aes.
# Exercise 2: Set a constant point colour outside aes and compare it with a group mapping.
# TODO: Inspect the built colour values.
# Exercise 3: Add a group-mean layer using its own data.
# TODO: Define the summary table and disable unwanted inherited mappings.
# Exercise 4: Diagnose aes(colour="group") when the intended mapping is the group column.
# TODO: Distinguish a string literal from a column expression.
# Exercise 5: Print a plot object from a script or function.
# TODO: Call print explicitly.
# Exercise 6: Explain what ggplot_build checks cannot establish about the delivered image.
# TODO: Separate layer data from visual perception.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
