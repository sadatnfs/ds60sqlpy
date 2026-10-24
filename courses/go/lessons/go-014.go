package main

import "fmt"

func main() {
	// Exercise 1: Build a named table: Test clamp with values below, inside and above the range 0 to 10.
	// Expected: The outputs are 0, 4 and 10.

	// Exercise 2: Include exact endpoints: Test clamp at 0 and 10.
	// Expected: Both endpoints are preserved.

	// Exercise 3: Check idempotence: Apply clamp twice to values -2, 4 and 12.
	// Expected: Applying it twice gives the same result as once.

	// Exercise 4: Reject a plausible mutant: Compare the correct clamp with a mutant that incorrectly caps at 9.
	// Expected: Input 10 distinguishes them.

	// Exercise 5: Cover a range invariant: Check all integer inputs from -20 through 20.
	// Expected: Every result lies between 0 and 10.

	// Exercise 6: Transfer a fresh regression: Retain input 11 as a regression for an implementation that forgets the upper cap.
	// Expected: The result is 10.

	fmt.Println("Implement the six investigations in your saved pad.")
}
