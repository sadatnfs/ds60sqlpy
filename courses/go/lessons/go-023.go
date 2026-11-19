package main

import "fmt"

func main() {
	// Exercise 1: Read a successful response: change one input: Copy worked example 1 into a scratch pad and change `v, err := fetch(context.Background(), 200, "ready", 8)` to `v, err := fetch(context.Background(), 201, "ready", 8)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `client success` because `err == nil && v == "ready"` no longer holds. Restoring the original line brings back the worked observation: the client helper returns ready without error.

	// Exercise 2: Reject an HTTP failure status: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(err == nil, "HTTP status")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `HTTP status`; after it the line reads `check(err != nil, "HTTP status")` again and the helper returns an error despite transport success.

	// Exercise 3: Detect an oversized body: Return five bytes with a maximum of four.
	// Expected: The helper rejects the response.

	// Exercise 4: Honor cancellation: Cancel the context before invoking the fake transport.
	// Expected: The returned error matches context.Canceled.

	// Exercise 5: Allow exact size: Return four bytes with a maximum of four.
	// Expected: The helper accepts all four bytes.

	// Exercise 6: Transfer an empty body: Return 200 with an empty body under a positive budget.
	// Expected: The transport helper returns an empty string successfully.

	fmt.Println("Implement the six investigations in your saved pad.")
}
