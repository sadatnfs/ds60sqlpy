package main

import "fmt"

func main() {
	// Exercise 1: Converge from a different state: change one input: Copy worked example 1 into a scratch pad and change `err := reconcileCap(context.Background(), &s, "u1", 3)` to `err := reconcileCap(context.Background(), &s, "u1", 4)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `converge` because `err == nil && s.Current == 3 && s.Writes == 1` no longer holds. Restoring the original line brings back the worked observation: the count becomes 3 with one write.

	// Exercise 2: Repeat without duplicate writes: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(reconcileCap(context.Background(), &s, "u1", 4) == nil, "first")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `idempotent`; after it the line reads `check(reconcileCap(context.Background(), &s, "u1", 3) == nil, "first")` again and only the first call writes.

	// Exercise 3: Refuse a replacement object: Supply expected UID old while observed UID is new.
	// Expected: No write occurs and an ownership error is returned.

	// Exercise 4: Preserve state on invalid intent: Request a negative count.
	// Expected: The operation fails without mutation.

	// Exercise 5: Cancel before new work: Pass an already-canceled context.
	// Expected: No write occurs and cancellation is retained.

	// Exercise 6: Transfer restart reasoning: Copy the converged durable state into a new controller invocation.
	// Expected: The restarted invocation makes no additional write.

	fmt.Println("Implement the six investigations in your saved pad.")
}
