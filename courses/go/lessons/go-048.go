package main

import "fmt"

func main() {
	// Exercise 1: Converge from a different state: change one input: Copy worked example 1, change `err := reconcileCap(context.Background(), &s, "u1", 3)` to `err := reconcileCap(context.Background(), &s, "u1", 4)` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `converge` because `err == nil && s.Current == 3 && s.Writes == 1` no longer holds.

	// Exercise 2: Repeat without duplicate writes: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(reconcileCap(context.Background(), &s, "u1", 4) == nil, "first")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `idempotent`; after restoring `check(reconcileCap(context.Background(), &s, "u1", 3) == nil, "first")`, only the first call writes.

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
