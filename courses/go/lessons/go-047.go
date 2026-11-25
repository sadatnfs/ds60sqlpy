package main

import "fmt"

func main() {
	// Exercise 1: Verify one successful API call: change one input: Copy worked example 1, change `f := &FakeReader{Value: 3}` to `f := &FakeReader{Value: 4}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `success` because `err == nil && v == 3 && f.Calls == 1` no longer holds.

	// Exercise 2: Preserve a forbidden error: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(errors.Is(err, ErrForbidden) && f.Calls != 1, "forbidden")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `forbidden`; after restoring `check(errors.Is(err, ErrForbidden) && f.Calls == 1, "forbidden")`, the exact cause is visible and only one call occurs.

	// Exercise 3: Stop before a canceled call: Cancel context before invoking the adapter.
	// Expected: No API call is made.

	// Exercise 4: Distinguish returned zero from failure: Return a successful zero from the fake.
	// Expected: The zero is accepted with nil error.

	// Exercise 5: Retain an unknown failure: Return an unexpected error cause.
	// Expected: The cause remains inspectable.

	// Exercise 6: Transfer source-bound evidence: Bind a synthetic receipt to its lesson ID and the SHA-256 digest of the exact source text, then compare it with a source that has one extra byte.
	// Expected: The receipt matches the exact source and rejects the changed source.

	fmt.Println("Implement the six investigations in your saved pad.")
}
