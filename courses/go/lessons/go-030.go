package main

import "fmt"

func main() {
	// Exercise 1: Find a lower boundary: change one input: Copy worked example 1 into a scratch pad and change `items := []int{2, 4, 6, 8}` to `items := []int{2, 5, 6, 8}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `boundary` because `i == 2` no longer holds. Restoring the original line brings back the worked observation: the index is 2.

	// Exercise 2: Represent no match: debug a regression: A regression changed one token in worked example 2, so one line now reads `items := []int{2, 4, 6, 9}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `not found`; after it the line reads `items := []int{2, 4, 6, 8}` again and the index equals the collection length.

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
