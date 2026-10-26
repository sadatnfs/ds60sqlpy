# r-036: Chunked aggregation and memory-aware data contracts
# Complete the six guide tasks using these local inputs.
chunks <- list(10, c(20, 30, 40), numeric(0))
# TODO: retain mergeable state with an explicit finalization rule.
print(vapply(chunks, length, integer(1)))
