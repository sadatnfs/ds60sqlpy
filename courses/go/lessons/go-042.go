package main

import "fmt"

func main() {
	// Exercise 1: Copy before changing labels: change one input: Copy worked example 1, change `cached := Cached{Labels: map[string]string{"app": "web"}, Version: "a"}` to `cached := Cached{Labels: map[string]string{"app!": "web"}, Version: "a"}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `copy` because `cached.Labels["app"] == "web" && copy.Labels["app"] == "api"` no longer holds.

	// Exercise 2: Expose a shallow-copy defect safely: debug a regression: A one-token regression in worked example 2 makes a line read `shallow.Labels["app!"] = "bad"`. Repair it without changing the check.
	// Expected: The defective run panics with `shallow counterexample`; after restoring `shallow.Labels["app"] = "bad"`, the original observes the unintended change.

	// Exercise 3: Represent a stale view: Deliver only the first of two watch events to a cache that starts at version a.
	// Expected: The cache shows b while the server's latest version is already c.

	// Exercise 4: Gate on initial synchronization: Offer one item to a processor before and after the cache reports synced.
	// Expected: No item is processed before the cache reports synced; one item is processed afterward.

	// Exercise 5: Queue identities instead of objects: Queue the key of a cached object, then let the store receive a newer version before the key is processed.
	// Expected: The queued key reads the latest object, version b, not the snapshot taken when it was queued.

	// Exercise 6: Transfer nested-copy independence: Add a new label to a copied object.
	// Expected: The original label count is unchanged.

	fmt.Println("Implement the six investigations in your saved pad.")
}
