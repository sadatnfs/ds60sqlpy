package main

import "fmt"

func main() {
	// Exercise 1: Protect a concurrent count: Run four workers doing 100 protected increments each.
	// Expected: The joined final count is 400.

	// Exercise 2: Use a typed atomic: Add 3 and 4 through atomic.Int64.
	// Expected: Load returns 7.

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
