package main

import "fmt"

func main() {
	// Exercise 1: Match all required labels: predict an edited check: Copy worked example 1, change `matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` to `matches(map[string]string{"app!": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `match` even though `matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` still holds.

	// Exercise 2: Reject a missing label: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})`. Explain the failure, then restore it.
	// Expected: The defective run panics with `missing`; after restoring `!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})`, the selector does not match.

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
