package main

import "fmt"

func main() {
	// Exercise 1: Parse a quoted comma: predict an edited check: Copy worked example 1 into a scratch pad and change `check(err == nil && len(v) == 2 && v[1] == "Springfield, West", "quoted comma")` to `check(err == nil && len(v) == 3 && v[1] == "Springfield, West", "quoted comma")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `quoted comma` because the edited check no longer holds. Restoring the original line brings back the worked observation: the record contains two fields.

	// Exercise 2: Reject a ragged row: debug a regression: A regression changed one token in worked example 2, so one line now reads `r.FieldsPerRecord = 3`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `ragged row`; after it the line reads `r.FieldsPerRecord = 2` again and the reader reports a field-count error.

	// Exercise 3: Decode a numeric field: Parse the second field of item,12 as an integer.
	// Expected: The numeric value is 12.

	// Exercise 4: Reject blank numeric content: Attempt integer parsing of an empty field.
	// Expected: The conversion fails rather than becoming zero.

	// Exercise 5: Round-trip a delimiter field: Write a field containing a comma, flush, then read it back.
	// Expected: The original field survives exactly.

	// Exercise 6: Transfer header validation: Read the header name,count and compare its exact order.
	// Expected: The schema order is name then count.

	fmt.Println("Implement the six investigations in your saved pad.")
}
