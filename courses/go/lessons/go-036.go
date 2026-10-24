package main

import "fmt"

func main() {
	// Exercise 1: Match all required labels: Match app=web and tier=frontend against a Pod containing both.
	// Expected: The selector matches.

	// Exercise 2: Reject a missing label: Require tier when the Pod has only app.
	// Expected: The selector does not match.

	// Exercise 3: Distinguish empty value from absence: Require a present empty-valued label.
	// Expected: A present empty label matches; absence does not.

	// Exercise 4: Filter readiness separately: Select two matching Pods but admit only the ready one as usable.
	// Expected: Exactly one usable backend remains.

	// Exercise 5: Inspect an overly broad selector: Use an empty equality selector against two unrelated labels.
	// Expected: Both match this mathematical predicate.

	// Exercise 6: Transfer rollout-stable identity: Match app=web across two different rollout labels.
	// Expected: Both versions match the stable app selector.

	fmt.Println("Implement the six investigations in your saved pad.")
}
