package main

import "fmt"

func main() {
	// Exercise 1: Admit a required read: change one input: Copy worked example 1 into a scratch pad and change `rule := Rule{Namespace: "lesson", Resource: "pods", Verbs: []string{"get", "list", "watch"}}` to `rule := Rule{Namespace: "lesson!", Resource: "pods", Verbs: []string{"get", "list", "watch"}}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `read` because `allowed(rule, "lesson", "pods", "get")` no longer holds. Restoring the original line brings back the worked observation: the request is admitted by the local rule model.

	// Exercise 2: Reject an unneeded mutation: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(allowed(rule, "lesson", "pods", "delete"), "mutation")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `mutation`; after it the line reads `check(!allowed(rule, "lesson", "pods", "delete"), "mutation")` again and the request is rejected.

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
