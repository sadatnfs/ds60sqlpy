package main

import "fmt"

func main() {
	// Exercise 1: Trace a prefix sum: change one input: Copy worked example 1, change `items := []int{2, 4, 6}` to `items := []int{3, 4, 6}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `sum` because `sum == 12 && len(items) == 3` no longer holds.

	// Exercise 2: Handle empty data: debug a regression: A one-token regression in worked example 2 makes a line read `sum := 1`. Repair it without changing the check.
	// Expected: The defective run panics with `empty sum`; after restoring `sum := 0`, the result is 0 with no special invented element.

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
