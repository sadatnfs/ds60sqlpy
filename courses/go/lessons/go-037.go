package main

import "fmt"

func main() {
	// Exercise 1: Plan a missing child: predict an edited check: Copy worked example 1, change `check(plan(3, false, 0) == "create", "missing child")` to `check(plan(3, true, 0) == "create", "missing child")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `missing child` even though `plan(3, false, 0) == "create"` still holds.

	// Exercise 2: Plan a changed child: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(plan(3, true, 3) == "update", "changed child")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `changed child`; after restoring `check(plan(3, true, 2) == "update", "changed child")`, the action is update.

	// Exercise 3: Make convergence a no-op: Observe an existing child already at count 3.
	// Expected: The action is none.

	// Exercise 4: Reject invalid desired state: Supply a negative desired count.
	// Expected: The planner returns invalid.

	// Exercise 5: Simulate a converging step: Start at count 1, apply the planned update to 3 and plan again.
	// Expected: The next plan is none.

	// Exercise 6: Transfer scale-to-zero: Request zero for an existing child with count 2.
	// Expected: The planner requests update, then converges at zero.

	fmt.Println("Implement the six investigations in your saved pad.")
}
