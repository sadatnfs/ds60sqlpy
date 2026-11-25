package main

import "fmt"

func main() {
	// Exercise 1: Preserve input order: change one input: Copy worked example 1, change `v, err := parallelSquares([]int{3, 1, 2}, 2)` to `v, err := parallelSquares([]int{4, 1, 2}, 2)` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `order` because `err == nil && len(v) == 3 && v[0] == 9 && v[1] == 1 && v[2] == 4` no longer holds.

	// Exercise 2: Handle empty input: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(err != nil && len(v) == 0, "empty")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `empty`; after restoring `check(err == nil && len(v) == 0, "empty")`, it returns an empty result and terminates.

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
