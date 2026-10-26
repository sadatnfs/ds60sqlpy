# r-021: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

values <- c(3, 7)
unit <- "ms"

# Exercise 1: Trace measurement_total(measurement(c(3,7), "ms")).
# TODO: Name both the selected method and returned unit.
# Exercise 2: Add one observation five to the input and check that the earlier object is unchanged.
# TODO: Construct another value instead of modifying the earlier list.
# Exercise 3: Implement an observed-count generic for measurement objects.
# TODO: Use a distinct generic and class-specific method; keep validation.
# Exercise 4: Diagnose structure(list(values=c(1,Inf),unit="ms"), class="measurement").
# TODO: A class attribute is not a validator.
# Exercise 5: Define the empty-vector and empty-unit cases.
# TODO: The contract permits one of them.
# Exercise 6: Explain whether a measurement containing an environment would have the same copy guarantee.
# TODO: Distinguish the list container from a referenced component.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
