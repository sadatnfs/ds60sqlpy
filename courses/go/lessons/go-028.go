package main

import "fmt"

func main() {
	// Exercise 1: Preserve input order: Square 3, 1 and 2 with two workers.
	// Expected: The result is 9, 1, 4.

	// Exercise 2: Handle empty input: Run the pool on an empty slice.
	// Expected: It returns an empty result and terminates.

	// Exercise 3: Reject absent capacity: Request zero workers.
	// Expected: The call returns an error immediately.

	// Exercise 4: Compare serial semantics: Use one and three workers for the same three inputs.
	// Expected: Both produce the same sequence.

	// Exercise 5: Retain duplicate tasks: Process 2, 2 and 2.
	// Expected: All three results are retained.

	// Exercise 6: Transfer idle-worker cleanup: Use four workers for one input of 5.
	// Expected: One result equals 25 and all workers exit.

	fmt.Println("Implement the six investigations in your saved pad.")
}
