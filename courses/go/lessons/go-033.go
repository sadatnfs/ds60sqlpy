package main

import "fmt"

func main() {
	// Exercise 1: Commit a valid change: Transfer 3 between balances 5 and 5 in a staged transaction.
	// Expected: The committed balances are 2 and 8.

	// Exercise 2: Rollback an explicit failure: Change staged state and return an error.
	// Expected: The outer balances remain unchanged.

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
