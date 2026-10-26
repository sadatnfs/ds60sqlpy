# r-058: independent practice
# Supplied input fixture only; fill results and add independent assertions.

d <- data.frame(id = c("A1", "A2", "B1", "B2"), group = c("A", "A", "B", "B"), x = c(1, 2, 1, 2), y = c(2, 3, 4, 6))
results <- vector("list", 6L)

# Exercise 1: Attach stable observation IDs independently of x/y coordinates.
# TODO: Use customdata rather than inferring identity from array position.
# Exercise 2: Define a hover template with labels and units.
# TODO: State what each displayed field means.
# Exercise 3: Encode All and Group A visibility buttons for two known traces.
# TODO: Keep the visibility vector aligned with trace order.
# Exercise 4: Diagnose a global mean label that remains unchanged when a view hides one group.
# TODO: Determine whether the control recomputes statistics.
# Exercise 5: Provide a non-hover-dependent table or summary.
# TODO: Keep essential IDs and values visible in another channel.
# Exercise 6: Explain what remains unverified after inspecting the figure specification in R.
# TODO: Separate encoded controls from observed browser behavior.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
