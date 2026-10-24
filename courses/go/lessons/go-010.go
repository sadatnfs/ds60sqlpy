package main

import "fmt"

func main() {
	// Exercise 1: Dispatch through behavior: Store Counter with value 3 in a Valuer interface.
	// Expected: Calling Value returns 3.

	// Exercise 2: Mutate through a method: Call Add on a pointer to Counter starting at 3.
	// Expected: Its value becomes 5.

	// Exercise 3: Trace a value receiver: Call a value-receiver helper that increments only its receiver copy.
	// Expected: The returned value is 4 but the original remains 3.

	// Exercise 4: Expose typed nil: Put a nil pointer to Counter inside an empty interface.
	// Expected: The interface is not nil.

	// Exercise 5: Use safe dynamic inspection: Assert that an interface containing a string is an int with comma-ok.
	// Expected: The assertion reports false without panicking.

	// Exercise 6: Transfer substitutability: Implement a second Valuer type returning a fixed value and use the same consuming helper.
	// Expected: Both implementations can be read through one contract.

	fmt.Println("Implement the six investigations in your saved pad.")
}
