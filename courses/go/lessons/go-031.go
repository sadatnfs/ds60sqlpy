package main

import "fmt"

func main() {
	// Exercise 1: Emit a structured event: Log processed with count 3 and parse its JSON.
	// Expected: The record has message processed and numeric count 3.

	// Exercise 2: Retain correlation: Log request_id lesson-7.
	// Expected: The ID is retained exactly.

	// Exercise 3: Control variable time: Inspect the deterministic fixture record.
	// Expected: The time attribute is absent.

	// Exercise 4: Keep status structured: Log a failed status separately from its message.
	// Expected: status equals failed.

	// Exercise 5: Redact before logging: Replace a credential value with a fixed marker.
	// Expected: Only [redacted] is present.

	// Exercise 6: Transfer numeric evidence: Log a byte count of 12.
	// Expected: The parsed field remains numeric 12.

	fmt.Println("Implement the six investigations in your saved pad.")
}
