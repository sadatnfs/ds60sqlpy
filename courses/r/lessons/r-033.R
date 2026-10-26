# r-033: Joins, key uniqueness and unmatched records
# Complete the six guide tasks using these local inputs.
facts <- data.frame(product = c("B", "A", "C"), amount = c(10, 20, 30))
dimension <- data.frame(product = c("A", "B"), category = c("Paper", "Home"))
# TODO: validate cardinality and retain unmatched-key evidence.
print(facts)
