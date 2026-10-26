# r-035: Validate ingestion and preserve rejected-record evidence
# Complete the six guide tasks using these local inputs.
raw <- data.frame(id = c("A", "", "C", "D"), amount = c(2, 3, -1, NA_real_))
# TODO: retain rule flags and reconcile admitted/rejected counts.
print(raw)
