package main

import "fmt"

func main() {
	// Exercise 1: Parse a quoted comma: predict an edited check: Copy worked example 1, change `check(err == nil && len(v) == 2 && v[1] == "Springfield, West", "quoted comma")` to `check(err == nil && len(v) == 3 && v[1] == "Springfield, West", "quoted comma")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `quoted comma` even though `err == nil && len(v) == 2 && v[1] == "Springfield, West"` still holds.

	// Exercise 2: Reject a ragged row: debug a regression: A one-token regression in worked example 2 makes a line read `r.FieldsPerRecord = 3`. Repair it without changing the check.
	// Expected: The defective run panics with `ragged row`; after restoring `r.FieldsPerRecord = 2`, the reader reports a field-count error.

	// Exercise 3: Decode a numeric field: Parse the second field of item,12 as an integer.
	// Expected: The numeric value is 12.

	// Exercise 4: Reject blank numeric content: Attempt integer parsing of an empty field.
	// Expected: The conversion fails rather than becoming zero.

	// Exercise 5: Round-trip a delimiter field: Write a field containing a comma, flush, then read it back.
	// Expected: The original field survives exactly.

	// Exercise 6: Transfer header validation: Read the header `name,count` and compare its exact order.
	// Expected: The schema order is name then count.

	fmt.Println("Implement the six investigations in your saved pad.")
}
