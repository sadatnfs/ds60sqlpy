package main

import "fmt"

func main() {
	// Exercise 1: Model a coordinate: change one input: Copy worked example 1, change `p := Point{X: 2, Y: 3}` to `p := Point{X: 3, Y: 3}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `point` because `p.X+p.Y == 5` no longer holds.

	// Exercise 2: Observe scalar copy: debug a regression: A one-token regression in worked example 2 makes a line read `a := Point{X: 3, Y: 3}`. Repair it without changing the check.
	// Expected: The defective run panics with `struct copy`; after restoring `a := Point{X: 2, Y: 3}`, the original X remains 2.

	// Exercise 3: Expose a shallow field: Copy a Batch struct containing a slice and mutate its first item.
	// Expected: The original batch observes the mutation.

	// Exercise 4: Inspect zero state: Declare a Point without a literal.
	// Expected: Both coordinates are 0.

	// Exercise 5: Use a comparable key: Store a label keyed by Point and retrieve it with an equal Point.
	// Expected: The equal coordinate finds origin.

	// Exercise 6: Transfer validation: Construct a named item with an empty name and then a valid name.
	// Expected: The empty name is rejected; the valid name is retained.

	fmt.Println("Implement the six investigations in your saved pad.")
}
