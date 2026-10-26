# r-026: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

x <- c(1, 4, 9)
package_name <- "measurekit"
results <- vector("list", 6L)

# Exercise 1: Predict the difference between a global median and stats::median.
# TODO: Resolve the qualified call through the package export.
# Exercise 2: Retrieve the public median function without attaching stats names.
# TODO: Use getExportedValue with explicit package and name.
# Exercise 3: Create and inspect DESCRIPTION, NAMESPACE and one R source file in a temporary tree.
# TODO: Keep all paths below the owned temporary directory.
# Exercise 4: Diagnose a helper being considered private merely because its name starts with a dot.
# TODO: Naming convention is not the namespace export policy.
# Exercise 5: Test empty and nonfinite values in the local observed_mean function.
# TODO: The public contract permits an empty set but rejects an infinite measurement.
# Exercise 6: Describe what remains before claiming that the temporary tree is an installed, checked package.
# TODO: Parsing and sys.source do not perform package installation.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
