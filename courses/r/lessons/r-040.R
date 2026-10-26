# r-040: An auditable analytical pipeline capstone
# Complete the six guide tasks using these local inputs.
raw <- data.frame(id = c("R1", "R2", "R3", "R4"), segment = c("A", "B", "A", "B"), amount = c(10, 20, NA_real_, 40))
dimension <- data.frame(segment = c("A", "B"), label = c("Alpha", "Beta"))
# TODO: build a report with admission and reconciliation evidence.
print(raw)
