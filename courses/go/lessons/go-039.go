package main

import "fmt"

func main() {
	// Exercise 1: Apply an added object: predict an edited check: Copy worked example 1 into a scratch pad and change `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"})` to `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 3, Version: "a"})` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `add` because the edited check no longer holds. Restoring the original line brings back the worked observation: the cache gains demo=2.

	// Exercise 2: Apply a modification: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 4, Version: "b"})`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `modify`; after it the line reads `applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 3, Version: "b"})` again and the cached value becomes 3.

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
