package main

import "fmt"

func main() {
	// Exercise 1: Observe shared storage: change one input: Copy worked example 1, change `view[0] = 9` to `view[1] = 9` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `alias` because `values[0] == 9` no longer holds.

	// Exercise 2: Make an independent copy: debug a regression: A one-token regression in worked example 2 makes a line read `values := []int{2, 2, 3}`. Repair it without changing the check.
	// Expected: The defective run panics with `copy`; after restoring `values := []int{1, 2, 3}`, the original stays 1 while the copy starts 9.

	// Exercise 3: Restrict append capacity: Take values[:1:1] and append 8.
	// Expected: The original second element remains 2.

	// Exercise 4: Inspect a truncated copy: Copy three source elements into a length-two destination.
	// Expected: Exactly two elements are copied.

	// Exercise 5: Grow an empty slice: Append 7 to a nil slice.
	// Expected: The result has length 1 and value 7.

	// Exercise 6: Transfer array semantics: Copy a fixed array and mutate the copy.
	// Expected: The original array remains unchanged.

	fmt.Println("Implement the six investigations in your saved pad.")
}
