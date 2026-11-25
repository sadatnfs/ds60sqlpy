package main

import "fmt"

func main() {
	// Exercise 1: Apply an explicit flag: change one input: Copy worked example 1, change `n, args, err := parseArgs([]string{"-count=3"})` to `n, args, err := parseArgs([]string{"-count=4"})` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `flag` because `err == nil && n == 3 && len(args) == 0` no longer holds.

	// Exercise 2: Retain a default: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(err != nil && n == 1, "default")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `default`; after restoring `check(err == nil && n == 1, "default")`, the count remains 1.

	// Exercise 3: Reject an unknown option: Parse -mystery=2.
	// Expected: Parsing returns an error.

	// Exercise 4: Preserve positional arguments: Parse a count flag followed by a filename.
	// Expected: The remaining argument is input.csv.

	// Exercise 5: Reject a domain-invalid count: Parse -count=-1 and perform range validation.
	// Expected: The operation returns a domain error.

	// Exercise 6: Transfer precedence: Apply a flag override of 4 after a default value of 1.
	// Expected: The explicit setting wins.

	fmt.Println("Implement the six investigations in your saved pad.")
}
