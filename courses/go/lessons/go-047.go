package main

import "fmt"

func main() {
	// Exercise 1: Verify one successful API call: change one input: Copy worked example 1 into a scratch pad and change `f := &FakeReader{Value: 3}` to `f := &FakeReader{Value: 4}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `success` because `err == nil && v == 3 && f.Calls == 1` no longer holds. Restoring the original line brings back the worked observation: the result is retained and exactly one call occurs.

	// Exercise 2: Preserve a forbidden error: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(errors.Is(err, ErrForbidden) && f.Calls != 1, "forbidden")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `forbidden`; after it the line reads `check(errors.Is(err, ErrForbidden) && f.Calls == 1, "forbidden")` again and the exact cause is visible and only one call occurs.

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
