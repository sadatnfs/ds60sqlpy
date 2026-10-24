package main

import "fmt"

func main() {
	// Exercise 1: Parse a quoted comma: Read name and city where the city is Springfield, West.
	// Expected: The record contains two fields.

	// Exercise 2: Reject a ragged row: Require two fields and read a three-field row.
	// Expected: The reader reports a field-count error.

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
