package main

import "fmt"

func main() {
	// Exercise 1: Apply an added object: predict an edited check: Copy worked example 1, change `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"})` to `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 3, Version: "a"})` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `add` even though `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"}) == nil && s.Items["demo"] == 2` still holds.

	// Exercise 2: Apply a modification: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 4, Version: "b"})`. Explain the failure, then restore it.
	// Expected: The defective run panics with `modify`; after restoring `applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 3, Version: "b"})`, the cached value becomes 3.

	// Exercise 3: Advance a bookmark: Apply a bookmark without an object.
	// Expected: The version advances and no item is created.

	// Exercise 4: Invalidate expired continuity: Apply an expired-history signal.
	// Expected: The state requests a relist.

	// Exercise 5: Delete current membership: Delete an existing key and then delete it again.
	// Expected: The cache remains empty.

	// Exercise 6: Transfer unknown-event refusal: Apply an unsupported event kind.
	// Expected: An error is returned without accepting invented semantics.

	fmt.Println("Implement the six investigations in your saved pad.")
}
