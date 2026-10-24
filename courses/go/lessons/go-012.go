package main

import "fmt"

func main() {
	// Exercise 1: Trace cleanup order: Register first and second cleanup markers and return.
	// Expected: The observed order is second then first.

	// Exercise 2: Compare captured arguments: Defer a call with x as an argument, then change x.
	// Expected: The deferred argument retains the earlier value 1.

	// Exercise 3: Compare a closure read: Defer a closure reading x, then change x to 2.
	// Expected: The closure observes 2.

	// Exercise 4: Contain a deliberate panic: Panic with the known value broken inside a helper that recovers it.
	// Expected: The helper reports broken explicitly.

	// Exercise 5: Preserve cleanup during failure: Register cleanup and then panic inside a recovered helper.
	// Expected: The cleanup marker is still set.

	// Exercise 6: Transfer function-scoped cleanup: Run three helpers, each with its own deferred marker.
	// Expected: All three markers are present after the loop.

	fmt.Println("Implement the six investigations in your saved pad.")
}
