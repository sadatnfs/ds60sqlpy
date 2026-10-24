package main

import "fmt"

func main() {
	// Exercise 1: Accept a current version: Update value 2 using its current token a.
	// Expected: The value changes and token becomes b.

	// Exercise 2: Reject a stale version: Attempt a write with old token a against current token b.
	// Expected: Conflict is returned and value stays unchanged.

	// Exercise 3: Reread before retry: Read the current token after conflict and recompute an increment.
	// Expected: The new value is based on current state.

	// Exercise 4: Keep opaque tokens opaque: Use token rv:opaque rather than an integer.
	// Expected: Equality-based update succeeds.

	// Exercise 5: Retain another field: Change one scalar while keeping a separate owner label.
	// Expected: The unrelated label is unchanged.

	// Exercise 6: Transfer bounded conflict handling: Try the same stale token twice and count conflicts.
	// Expected: Both attempts conflict and neither changes state.

	fmt.Println("Implement the six investigations in your saved pad.")
}
