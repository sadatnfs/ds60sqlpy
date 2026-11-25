package main

import "fmt"

func main() {
	// Exercise 1: Find a lower boundary: change one input: Copy worked example 1, change `items := []int{2, 4, 6, 8}` to `items := []int{2, 5, 6, 8}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `boundary` because `i == 2` no longer holds.

	// Exercise 2: Represent no match: debug a regression: A one-token regression in worked example 2 makes a line read `items := []int{2, 4, 6, 9}`. Repair it without changing the check.
	// Expected: The defective run panics with `not found`; after restoring `items := []int{2, 4, 6, 8}`, the index equals the collection length.

	// Exercise 3: Separate length and capacity: Reserve capacity four, then append one value.
	// Expected: Length is 1, capacity is 4.

	// Exercise 4: Count linear work: Sum five values and count visits.
	// Expected: There are five visits and the sum is 15.

	// Exercise 5: Handle empty search: Search a zero-length interval.
	// Expected: Index is 0 and the predicate is never called.

	// Exercise 6: Transfer duplicate boundaries: Find the first value at least 3 in 1, 3, 3, 5.
	// Expected: The first duplicate has index 1.

	fmt.Println("Implement the six investigations in your saved pad.")
}
