package main

import "fmt"

func main() {
	// Exercise 1: Commit a valid change: change one input: Copy worked example 1, change `s := Balances{A: 5, B: 5}` to `s := Balances{A: 6, B: 5}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `commit` because `err == nil && s.A == 2 && s.B == 8` no longer holds.

	// Exercise 2: Rollback an explicit failure: debug a regression: A one-token regression in worked example 2 makes a line read `s := Balances{A: 6, B: 5}`. Repair it without changing the check.
	// Expected: The defective run panics with `rollback`; after restoring `s := Balances{A: 5, B: 5}`, the outer balances remain unchanged.

	// Exercise 3: Reject invalid funds: Attempt a transfer larger than available balance.
	// Expected: The state remains 5 and 5.

	// Exercise 4: Preserve total value: Apply two successful transfers and inspect the combined balance.
	// Expected: The total remains 10.

	// Exercise 5: Keep a failed retry distinct: Fail one transaction, then explicitly start a new valid transaction.
	// Expected: Only the second change commits.

	// Exercise 6: Transfer no-op semantics: Run a transaction that changes nothing.
	// Expected: The state is preserved and the operation succeeds.

	fmt.Println("Implement the six investigations in your saved pad.")
}
