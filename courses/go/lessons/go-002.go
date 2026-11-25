package main

import "fmt"

func main() {
	// Exercise 1: Compare two divisions: change one input: Copy worked example 1, change `a := 7 / 2` to `a := 8 / 2` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `division` because `a == 3 && b == 3.5` no longer holds.

	// Exercise 2: Expose narrowing: debug a regression: A one-token regression in worked example 2 makes a line read `n := 261`. Repair it without changing the check.
	// Expected: The defective run panics with `narrowing`; after restoring `n := 260`, the narrowed value is 4.

	// Exercise 3: Preserve a wide product: Multiply two explicitly int64 values of 50000.
	// Expected: The product is 2500000000.

	// Exercise 4: Check approximate arithmetic: Add floating variables 0.1 and 0.2 and compare with a 1e-15 tolerance.
	// Expected: The absolute difference from 0.3 is below 1e-15.

	// Exercise 5: Reject invalid numeric text: Parse the text 12x as a base-ten signed integer.
	// Expected: Parsing returns a non-nil error.

	// Exercise 6: Transfer signed division: Divide -7 by 2 and compute its remainder.
	// Expected: The quotient is -3 and the remainder is -1.

	fmt.Println("Implement the six investigations in your saved pad.")
}
