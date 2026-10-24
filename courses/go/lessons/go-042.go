package main

import "fmt"

func main() {
	// Exercise 1: Copy before changing labels: Copy a cached object and change its app label.
	// Expected: The cache still contains the original label.

	// Exercise 2: Expose a shallow-copy defect safely: Assign a struct containing a map and mutate the assigned map sequentially.
	// Expected: The original observes the unintended change.

	// Exercise 3: Represent a stale view: Keep cache version a while a server model has version b.
	// Expected: The versions differ without implying a failed write.

	// Exercise 4: Gate on initial synchronization: Inspect a false cache-synced flag before processing.
	// Expected: The worker does not claim readiness.

	// Exercise 5: Queue identities instead of objects: Store a namespace/name key derived from a snapshot.
	// Expected: The key remains usable after the object value changes.

	// Exercise 6: Transfer nested-copy independence: Add a new label to a copied object.
	// Expected: The original label count is unchanged.

	fmt.Println("Implement the six investigations in your saved pad.")
}
