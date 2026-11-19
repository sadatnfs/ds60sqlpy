package main

import "fmt"

func main() {
	// Exercise 1: Match all required labels: predict an edited check: Copy worked example 1 into a scratch pad and change `matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` to `matches(map[string]string{"app!": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `match` because the edited check no longer holds. Restoring the original line brings back the worked observation: the selector matches.

	// Exercise 2: Reject a missing label: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `missing`; after it the line reads `!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})` again and the selector does not match.

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
