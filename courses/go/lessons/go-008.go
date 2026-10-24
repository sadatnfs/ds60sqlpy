package main

import "fmt"

func main() {
	// Exercise 1: Model a coordinate: Construct Point with X 2 and Y 3 and calculate Manhattan distance from the origin.
	// Expected: The distance is 5.

	// Exercise 2: Observe scalar copy: Copy a Point and change the copied X field.
	// Expected: The original X remains 2.

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
