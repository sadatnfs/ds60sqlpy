package main

import "fmt"

func main() {
	// Exercise 1: Trace cleanup order: predict an edited check: Copy worked example 1 into a scratch pad and change `check(deferOrder() == "second,first", "defer order")` to `check(deferOrder() == "second,first!", "defer order")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `defer order` because the edited check no longer holds. Restoring the original line brings back the worked observation: the observed order is second then first.

	// Exercise 2: Compare captured arguments: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(deferArgument() != 1, "argument evaluation")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `argument evaluation`; after it the line reads `check(deferArgument() == 1, "argument evaluation")` again and the deferred argument retains the earlier value 1.

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
