package main

import "fmt"

func main() {
	// Exercise 1: Protect a concurrent count: change one input: Copy worked example 1, change `for i := 0; i < 4; i++ {` to `for i := 1; i < 4; i++ {` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `count` because `c.Value() == 400` no longer holds.

	// Exercise 2: Use a typed atomic: debug a regression: A regression changed `n.Add(3)` to `n.Add(4)` in worked example 2. Repair it without changing the check.
	// Expected: The defective run panics with `atomic`; after restoring `n.Add(3)`, load returns 7.

	// Exercise 3: Protect a pair relationship: Transfer 3 between two balances initially 5 and 5.
	// Expected: The balances become 2 and 8; their sum remains 10.

	// Exercise 4: Initialize once: Call the same sync.Once initializer three times.
	// Expected: Its body runs once.

	// Exercise 5: Reject a stale atomic expectation: Perform compare-and-swap twice using the original expected value.
	// Expected: The first succeeds and the second fails.

	// Exercise 6: Transfer safe observation: Read an unchanged protected pair twice.
	// Expected: Both snapshots preserve total 10.

	fmt.Println("Implement the six investigations in your saved pad.")
}
