package main

import "fmt"

func main() {
	// Exercise 1: Use a package boundary: Join logical slash-separated path segments with path.Join.
	// Expected: The result is reports/daily.json.

	// Exercise 2: Compose standard-library APIs: Trim and parse the text containing spaces around 12.
	// Expected: The parsed value is 12.

	// Exercise 3: Inspect exported spelling: Compare a public API spelling with its lower-case variant as identifiers in a naming check.
	// Expected: The public spelling begins with an uppercase rune.

	// Exercise 4: Keep logical imports separate: Clean a logical path containing a parent component.
	// Expected: reports/tmp/../daily becomes reports/daily.

	// Exercise 5: Reject malformed input at an API boundary: Parse a nonnumeric public input after trimming.
	// Expected: The numeric error remains non-nil.

	// Exercise 6: Transfer an API contract: Build a deterministic report name from a validated positive integer.
	// Expected: The resulting logical name is reports/day-3.json.

	fmt.Println("Implement the six investigations in your saved pad.")
}
