package main

import "fmt"

func main() {
	// Exercise 1: Model a coordinate: change one input: Copy worked example 1 into a scratch pad and change `p := Point{X: 2, Y: 3}` to `p := Point{X: 3, Y: 3}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `point` because `p.X+p.Y == 5` no longer holds. Restoring the original line brings back the worked observation: the distance is 5.

	// Exercise 2: Observe scalar copy: debug a regression: A regression changed one token in worked example 2, so one line now reads `a := Point{X: 3, Y: 3}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `struct copy`; after it the line reads `a := Point{X: 2, Y: 3}` again and the original X remains 2.

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
