package main

import "fmt"

func main() {
	// Exercise 1: Apply an added object: Apply ADDED for demo with value 2.
	// Expected: The cache gains demo=2.

	// Exercise 2: Apply a modification: Add then modify the same key.
	// Expected: The cached value becomes 3.

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
