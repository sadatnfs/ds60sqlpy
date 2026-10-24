package main

import "fmt"

func main() {
	// Exercise 1: Accept a valid range: Validate replica count 3 under maximum 5.
	// Expected: The decision allows the request.

	// Exercise 2: Reject a negative value: Validate replica count -1.
	// Expected: The decision denies it with a reason.

	// Exercise 3: Check the exact upper boundary: Validate counts 5 and 6 against maximum 5.
	// Expected: Five is allowed and six is denied.

	// Exercise 4: Preserve request identity: Validate a request and inspect the response UID.
	// Expected: The exact request UID is copied.

	// Exercise 5: Keep dry-run side effects absent: Evaluate the same policy in dry-run mode.
	// Expected: The decision is computed with zero external effects.

	// Exercise 6: Transfer missing identity refusal: Evaluate a request lacking its UID.
	// Expected: The decision is denied.

	fmt.Println("Implement the six investigations in your saved pad.")
}
