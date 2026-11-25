package main

import "fmt"

func main() {
	// Exercise 1: Accept a current version: change one input: Copy worked example 1, change `err := versionUpdate(&s, "a", 3, "b")` to `err := versionUpdate(&s, "a", 4, "b")` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `current update` because `err == nil && s.Value == 3 && s.Version == "b"` no longer holds.

	// Exercise 2: Reject a stale version: debug a regression: A one-token regression in worked example 2 makes a line read `s := Versioned{Value: 4, Version: "b"}`. Repair it without changing the check.
	// Expected: The defective run panics with `conflict`; after restoring `s := Versioned{Value: 3, Version: "b"}`, conflict is returned and value stays unchanged.

	// Exercise 3: Reread before retry: Read the current token after conflict and recompute an increment.
	// Expected: The new value is based on current state.

	// Exercise 4: Keep opaque tokens opaque: Use token rv:opaque rather than an integer.
	// Expected: Equality-based update succeeds.

	// Exercise 5: Retain another field: Update the value of an object that also carries an owner label, using its current token.
	// Expected: The value and token change while the owner label is unchanged.

	// Exercise 6: Transfer bounded conflict handling: Try the same stale token twice and count conflicts.
	// Expected: Both attempts conflict and neither changes state.

	fmt.Println("Implement the six investigations in your saved pad.")
}
