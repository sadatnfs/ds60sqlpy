package main

import "fmt"

func main() {
	// Exercise 1: Verify one successful API call: Run a fake client configured to return a value.
	// Expected: The result is retained and exactly one call occurs.

	// Exercise 2: Preserve a forbidden error: Make the fake return ErrForbidden.
	// Expected: The exact cause is visible and only one call occurs.

	// Exercise 3: Stop before a canceled call: Cancel context before invoking the adapter.
	// Expected: No API call is made.

	// Exercise 4: Distinguish returned zero from failure: Return a successful zero from the fake.
	// Expected: The zero is accepted with nil error.

	// Exercise 5: Retain an unknown failure: Return an unexpected error cause.
	// Expected: The cause remains inspectable.

	// Exercise 6: Transfer source-bound evidence: Bind a synthetic receipt to its lesson ID and source digest label.
	// Expected: Both identifiers survive comparison.

	fmt.Println("Implement the six investigations in your saved pad.")
}
