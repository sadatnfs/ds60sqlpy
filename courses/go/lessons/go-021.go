package main

import "fmt"

func main() {
	// Exercise 1: Apply an explicit flag: Parse -count=3 with a default of 1.
	// Expected: The resulting count is 3.

	// Exercise 2: Retain a default: Parse no arguments.
	// Expected: The count remains 1.

	// Exercise 3: Reject an unknown option: Parse -mystery=2.
	// Expected: Parsing returns an error.

	// Exercise 4: Preserve positional arguments: Parse a count flag followed by a filename.
	// Expected: The remaining argument is input.csv.

	// Exercise 5: Reject a domain-invalid count: Parse -count=-1 and perform range validation.
	// Expected: The operation returns a domain error.

	// Exercise 6: Transfer precedence: Apply a flag override of 4 after a default value of 1.
	// Expected: The explicit setting wins.

	fmt.Println("Implement the six investigations in your saved pad.")
}
