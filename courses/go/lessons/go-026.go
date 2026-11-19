package main

import "fmt"

func main() {
	// Exercise 1: Cancel a child: predict an edited check: Copy worked example 1 into a scratch pad and change `check(ctx.Err() == context.Canceled, "cancel")` to `check(ctx.Err() != context.Canceled, "cancel")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `cancel` because the edited check no longer holds. Restoring the original line brings back the worked observation: err returns context.Canceled.

	// Exercise 2: Propagate parent cancellation: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(parent.Err() != context.Canceled && child.Err() == context.Canceled, "tree")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `tree`; after it the line reads `check(parent.Err() == context.Canceled && child.Err() == context.Canceled, "tree")` again and both contexts become canceled.

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
