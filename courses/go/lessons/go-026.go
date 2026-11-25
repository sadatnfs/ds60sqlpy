package main

import "fmt"

func main() {
	// Exercise 1: Cancel a child: predict an edited check: Copy worked example 1, change `check(ctx.Err() == context.Canceled, "cancel")` to `check(ctx.Err() != context.Canceled, "cancel")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `cancel` even though `ctx.Err() == context.Canceled` still holds.

	// Exercise 2: Propagate parent cancellation: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(parent.Err() != context.Canceled && child.Err() == context.Canceled, "tree")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `tree`; after restoring `check(parent.Err() == context.Canceled && child.Err() == context.Canceled, "tree")`, both contexts become canceled.

	// Exercise 3: Keep child cancellation local: Cancel a child of a live parent.
	// Expected: The child is canceled; the parent is unchanged.

	// Exercise 4: Test an expired deadline: Construct a context with a deadline at Unix time zero.
	// Expected: Err is context.DeadlineExceeded.

	// Exercise 5: Refuse already canceled work: Call a helper that checks its context before calculation.
	// Expected: It returns cancellation without a result.

	// Exercise 6: Transfer successful work: Use the same helper with a live context.
	// Expected: It returns 8 without error.

	fmt.Println("Implement the six investigations in your saved pad.")
}
