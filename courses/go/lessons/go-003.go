package main

import "fmt"

func main() {
	// Exercise 1: Trace a prefix sum: change one input: Copy worked example 1 into a scratch pad and change `items := []int{2, 4, 6}` to `items := []int{3, 4, 6}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `sum` because `sum == 12 && len(items) == 3` no longer holds. Restoring the original line brings back the worked observation: the final sum is 12 and three elements were visited.

	// Exercise 2: Handle empty data: debug a regression: A regression changed one token in worked example 2, so one line now reads `sum := 1`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `empty sum`; after it the line reads `sum := 0` again and the result is 0 with no special invented element.

	// Exercise 3: Use a safe guard: Guard access to the first element of an empty slice with a length check.
	// Expected: The condition is false and no indexing occurs.

	// Exercise 4: Find the first match: Find the first 8 in 3, 8, 8.
	// Expected: Its index is 1.

	// Exercise 5: Classify an exact boundary: Classify a score of 60 as pass using a threshold of 60.
	// Expected: The boundary belongs to the passing branch.

	// Exercise 6: Transfer to a filtered count: Count nonnegative values in -2, 0, 4 and -1.
	// Expected: Exactly 2 values satisfy the predicate.

	fmt.Println("Implement the six investigations in your saved pad.")
}
