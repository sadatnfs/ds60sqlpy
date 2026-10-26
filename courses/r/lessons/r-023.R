# r-023: independent practice
# Supplied inputs only; implement the contracts and add independent assertions.

initial <- 2
increment <- 3
results <- vector("list", 6L)

# Exercise 1: Predict two readings after a=Counter$new(2), b=a and b$add(3).
# TODO: Trace identity rather than copying the scalar mentally.
# Exercise 2: Make a separate scalar counter with clone and add four.
# TODO: Clone before mutating.
# Exercise 3: Verify that a rejected negative increment leaves the counter unchanged.
# TODO: Read before and after catching the specific validation error.
# Exercise 4: Construct a box containing a Counter and compare shallow and deep copies.
# TODO: The outer box can differ while its inner counter is shared.
# Exercise 5: Diagnose using one mutable counter for every resampling fold.
# TODO: A prior fold may leave state for the next.
# Exercise 6: State the limit of clone(deep=TRUE) for an arbitrary environment member.
# TODO: R6 members and all reference types are not interchangeable.

cat("Scaffold initialized; complete the six tasks and their checks.\n")
