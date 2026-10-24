package main

import "fmt"

func main() {
	// Exercise 1: Calculate increasing delay: Inspect attempts 0, 1 and 2.
	// Expected: The delays are 1, 2 and 4 units.

	// Exercise 2: Cap the delay: Inspect attempts beyond the configured cap.
	// Expected: The delay never exceeds 8 units.

	// Exercise 3: Coalesce duplicate keys: Enqueue alpha twice and beta once in a set model.
	// Expected: There are two pending identities.

	// Exercise 4: Separate invalid from transient: Classify a validation failure and a timeout-like failure.
	// Expected: Only the transient class is retried.

	// Exercise 5: Reset successful history: Clear a key after successful reconciliation.
	// Expected: Its next failure starts at the first delay.

	// Exercise 6: Transfer a total budget: Allow at most three attempts and count admitted retries.
	// Expected: Exactly three attempts are admitted.

	fmt.Println("Implement the six investigations in your saved pad.")
}
