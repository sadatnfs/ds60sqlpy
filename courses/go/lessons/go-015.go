package main

import "fmt"

func main() {
	// Exercise 1: Reuse an element contract: Call first with an integer slice and a string slice.
	// Expected: The results are 4 and red with presence true.

	// Exercise 2: Handle a generic empty value: Call first with an empty integer slice.
	// Expected: The result is zero with presence false.

	// Exercise 3: Preserve stable uniqueness: Deduplicate 2, 1, 2 while preserving first occurrence.
	// Expected: The result is 2 then 1.

	// Exercise 4: Admit a named underlying type: Sum two values of a named Count type.
	// Expected: The result is Count(7).

	// Exercise 5: Test the empty sum identity: Sum an empty int64 slice.
	// Expected: The result is int64 zero.

	// Exercise 6: Transfer equality semantics: Deduplicate strings with different case.
	// Expected: Red and red remain distinct.

	fmt.Println("Implement the six investigations in your saved pad.")
}
