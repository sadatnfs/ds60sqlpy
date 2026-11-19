package main

import "fmt"

func main() {
	// Exercise 1: Preserve a cause: change one input: Copy worked example 1 into a scratch pad and change `err := fmt.Errorf("read record: %w", ErrMissing)` to `err := fmt.Errorf("read record: %v", ErrMissing)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `wrapped cause` because `errors.Is(err, ErrMissing)` no longer holds. Restoring the original line brings back the worked observation: errors.Is still recognizes ErrMissing.

	// Exercise 2: Reject text equality: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(errors.Is(a, b), "identity not text")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `identity not text`; after it the line reads `check(!errors.Is(a, b), "identity not text")` again and their identities differ.

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
