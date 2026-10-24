package main

import "fmt"

func main() {
	// Exercise 1: Capture a changing variable: Create a closure referring to factor, change factor, then call it.
	// Expected: The closure uses the new factor 3.

	// Exercise 2: Create independent counters: Construct two counter closures and call the first twice.
	// Expected: The first returns 1 then 2; the second starts at 1.

	// Exercise 3: Inject a transformation: Map a doubling callback over 1, 2 and 3.
	// Expected: The result is 2, 4 and 6.

	// Exercise 4: Stop a visitor early: Visit 1 through 5 and stop after observing 3.
	// Expected: Exactly three values are visited.

	// Exercise 5: Handle an empty traversal: Visit an empty range with a callback that would increment a count.
	// Expected: The callback is never invoked.

	// Exercise 6: Transfer explicit state: Collect only even values from a bounded visitor.
	// Expected: The collected values are 2 and 4.

	fmt.Println("Implement the six investigations in your saved pad.")
}
