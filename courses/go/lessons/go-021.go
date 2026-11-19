package main

import "fmt"

func main() {
	// Exercise 1: Apply an explicit flag: change one input: Copy worked example 1 into a scratch pad and change `n, args, err := parseArgs([]string{"-count=3"})` to `n, args, err := parseArgs([]string{"-count=4"})`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `flag` because `err == nil && n == 3 && len(args) == 0` no longer holds. Restoring the original line brings back the worked observation: the resulting count is 3.

	// Exercise 2: Retain a default: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(err != nil && n == 1, "default")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `default`; after it the line reads `check(err == nil && n == 1, "default")` again and the count remains 1.

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
