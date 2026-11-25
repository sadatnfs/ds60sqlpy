package main

import "fmt"

func main() {
	// Exercise 1: Admit a required read: change one input: Copy worked example 1, change `rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get", "list", "watch"}}` to `rule := Rule{Namespace: "lesson!", Resource: "pods", Verbs: []string{"get", "list", "watch"}}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `read` because `allowed(rule, "lesson", "pods", "get")` no longer holds.

	// Exercise 2: Reject an unneeded mutation: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(allowed(rule, "lesson", "pods", "delete"), "mutation")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `mutation`; after restoring `check(!allowed(rule, "lesson", "pods", "delete"), "mutation")`, the request is rejected.

	// Exercise 3: Reject cross-namespace access: Use the lesson rule against another namespace.
	// Expected: The local model rejects it.

	// Exercise 4: Separate resource and subresource: Grant update on deployments/status but request update on deployments.
	// Expected: The whole-object update is rejected.

	// Exercise 5: Treat secret reads as authority: Check a pods-only rule against secrets.
	// Expected: Secret read access is rejected.

	// Exercise 6: Transfer verb distinction: Grant list but not watch and inspect both.
	// Expected: Only list is admitted.

	fmt.Println("Implement the six investigations in your saved pad.")
}
