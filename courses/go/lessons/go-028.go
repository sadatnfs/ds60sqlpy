package main

import "fmt"

func main() {
	// Exercise 1: Preserve input order: change one input: Copy worked example 1 into a scratch pad and change `v, err := parallelSquares([]int{3, 1, 2}, 2)` to `v, err := parallelSquares([]int{4, 1, 2}, 2)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `order` because `err == nil && len(v) == 3 && v[0] == 9 && v[1] == 1 && v[2] == 4` no longer holds. Restoring the original line brings back the worked observation: the result is 9, 1, 4.

	// Exercise 2: Handle empty input: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(err != nil && len(v) == 0, "empty")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `empty`; after it the line reads `check(err == nil && len(v) == 0, "empty")` again and it returns an empty result and terminates.

	// Exercise 3: Reject absent capacity: Request zero workers.
	// Expected: The call returns an error immediately.

	// Exercise 4: Compare serial semantics: Use one and three workers for the same three inputs.
	// Expected: Both produce the same sequence.

	// Exercise 5: Retain duplicate tasks: Process 2, 2 and 2.
	// Expected: All three results are retained.

	// Exercise 6: Transfer idle-worker cleanup: Use four workers for one input of 5.
	// Expected: One result equals 25 and all workers exit.

	fmt.Println("Implement the six investigations in your saved pad.")
}
