package main

import "fmt"

func main() {
	// Exercise 1: Preserve a cause: change one input: Copy worked example 1, change `err := fmt.Errorf("read record: %w", ErrMissing)` to `err := fmt.Errorf("read record: %v", ErrMissing)` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `wrapped cause` because `errors.Is(err, ErrMissing)` no longer holds.

	// Exercise 2: Reject text equality: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(errors.Is(a, b), "identity not text")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `identity not text`; after restoring `check(!errors.Is(a, b), "identity not text")`, their identities differ.

	// Exercise 3: Inspect a typed boundary: Return a LimitError carrying an allowed maximum and inspect it with errors.As.
	// Expected: The extracted limit is 3.

	// Exercise 4: Handle successful parsing: Parse valid integer text and check error before value use.
	// Expected: The result is 42 and the error is nil.

	// Exercise 5: Classify invalid parsing: Parse malformed integer text and inspect its NumError.
	// Expected: The typed parse error is present.

	// Exercise 6: Transfer joined failures: Join missing and permission errors and inspect both causes.
	// Expected: Both sentinels remain discoverable.

	fmt.Println("Implement the six investigations in your saved pad.")
}
