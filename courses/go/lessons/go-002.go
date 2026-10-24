package main

import "fmt"

func main() {
	// Exercise 1: Compare two divisions: Compute 7/2 and float64(7)/2.
	// Expected: The results are 3 and 3.5.

	// Exercise 2: Expose narrowing: Convert a variable holding 260 to uint8.
	// Expected: The narrowed value is 4.

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
