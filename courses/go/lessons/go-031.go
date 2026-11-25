package main

import "fmt"

func main() {
	// Exercise 1: Emit a structured event: change one input: Copy worked example 1, change `v := logRecord("processed", "count", 3)` to `v := logRecord("processed", "count", 4)` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `fields` because `v["msg"] == "processed" && v["count"] == float64(3)` no longer holds.

	// Exercise 2: Retain correlation: debug a regression: A one-token regression in worked example 2 makes a line read `v := logRecord("read", "request_id!", "lesson-7")`. Repair it without changing the check.
	// Expected: The defective run panics with `correlation`; after restoring `v := logRecord("read", "request_id", "lesson-7")`, the ID is retained exactly.

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
