package main

import "fmt"

func main() {
	// Exercise 1: Commit a valid change: change one input: Copy worked example 1 into a scratch pad and change `s := Balances{A: 5, B: 5}` to `s := Balances{A: 6, B: 5}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `commit` because `err == nil && s.A == 2 && s.B == 8` no longer holds. Restoring the original line brings back the worked observation: the committed balances are 2 and 8.

	// Exercise 2: Rollback an explicit failure: debug a regression: A regression changed one token in worked example 2, so one line now reads `s := Balances{A: 6, B: 5}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `rollback`; after it the line reads `s := Balances{A: 5, B: 5}` again and the outer balances remain unchanged.

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
