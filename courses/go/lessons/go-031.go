package main

import "fmt"

func main() {
	// Exercise 1: Emit a structured event: change one input: Copy worked example 1 into a scratch pad and change `v := logRecord("processed", "count", 3)` to `v := logRecord("processed", "count", 4)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `fields` because `v["msg"] == "processed" && v["count"] == float64(3)` no longer holds. Restoring the original line brings back the worked observation: the record has message processed and numeric count 3.

	// Exercise 2: Retain correlation: debug a regression: A regression changed one token in worked example 2, so one line now reads `v := logRecord("read", "request_id!", "lesson-7")`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `correlation`; after it the line reads `v := logRecord("read", "request_id", "lesson-7")` again and the ID is retained exactly.

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
