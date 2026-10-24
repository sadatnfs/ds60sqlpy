package main

import "fmt"

func main() {
	// Exercise 1: Publish through a channel: Send an initialized record from a goroutine.
	// Expected: The reader observes count 3 and ready true.

	// Exercise 2: Publish through closure: Write 7 before closing done, then read after receiving done.
	// Expected: The reader observes 7.

	// Exercise 3: Publish an atomic value: Store a complete record in atomic.Value.
	// Expected: The loaded record has count 4.

	// Exercise 4: Retain a previous snapshot: Load a value, then replace the stored value.
	// Expected: The old copy remains 4 and the current value is 5.

	// Exercise 5: Copy reference-containing data: Copy a slice before mutating the original.
	// Expected: The snapshot retains its original first element.

	// Exercise 6: Transfer local construction: Build a result string inside a worker and send the completed value.
	// Expected: The reader receives ready:3.

	fmt.Println("Implement the six investigations in your saved pad.")
}
