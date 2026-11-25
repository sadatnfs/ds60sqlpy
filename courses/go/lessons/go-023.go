package main

import "fmt"

func main() {
	// Exercise 1: Read a successful response: change one input: Copy worked example 1, change `v, err := fetch(context.Background(), 200, "ready", 8)` to `v, err := fetch(context.Background(), 201, "ready", 8)` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `client success` because `err == nil && v == "ready"` no longer holds.

	// Exercise 2: Reject an HTTP failure status: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(err == nil, "HTTP status")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `HTTP status`; after restoring `check(err != nil, "HTTP status")`, the helper returns an error despite transport success.

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
