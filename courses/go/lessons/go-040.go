package main

import "fmt"

func main() {
	// Exercise 1: Calculate increasing delay: predict an edited check: Copy worked example 1, change `check(delay(0) == 1 && delay(1) == 2 && delay(2) == 4, "growth")` to `check(delay(1) == 1 && delay(1) == 2 && delay(2) == 4, "growth")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `growth` even though `delay(0) == 1 && delay(1) == 2 && delay(2) == 4` still holds.

	// Exercise 2: Cap the delay: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(delay(3) != 8 && delay(10) == 8, "cap")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `cap`; after restoring `check(delay(3) == 8 && delay(10) == 8, "cap")`, the delay never exceeds 8 units.

	// Exercise 3: Coalesce duplicate keys: Enqueue alpha twice and beta once in a set model.
	// Expected: There are two pending identities.

	// Exercise 4: Separate invalid from transient: Classify a validation failure and a timeout-like failure.
	// Expected: Only the transient class is retried.

	// Exercise 5: Reset successful history: Clear a key after successful reconciliation.
	// Expected: Its next failure starts at the first delay.

	// Exercise 6: Transfer a total budget: Spend a total waiting budget of 10 units on retries whose delays come from delay(attempt).
	// Expected: Three retries fit (1+2+4=7 units); the fourth delay of 8 would exceed the budget.

	fmt.Println("Implement the six investigations in your saved pad.")
}
