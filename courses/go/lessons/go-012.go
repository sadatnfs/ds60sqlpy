package main

import "fmt"

func main() {
	// Exercise 1: Trace cleanup order: predict an edited check: Copy worked example 1, change `check(deferOrder() == "second,first", "defer order")` to `check(deferOrder() == "second,first!", "defer order")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `defer order` even though `deferOrder() == "second,first"` still holds.

	// Exercise 2: Compare captured arguments: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(deferArgument() != 1, "argument evaluation")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `argument evaluation`; after restoring `check(deferArgument() == 1, "argument evaluation")`, the deferred argument retains the earlier value 1.

	// Exercise 3: Compare a closure read: Defer a closure reading x, then change x to 2.
	// Expected: The closure observes 2.

	// Exercise 4: Contain a deliberate panic: Panic with the known value broken inside a helper that recovers it.
	// Expected: The helper reports broken explicitly.

	// Exercise 5: Preserve cleanup during failure: Register cleanup and then panic inside a recovered helper.
	// Expected: The cleanup marker is still set.

	// Exercise 6: Transfer function-scoped cleanup: Run three helpers, each with its own deferred marker.
	// Expected: All three markers are present after the loop.

	fmt.Println("Implement the six investigations in your saved pad.")
}
