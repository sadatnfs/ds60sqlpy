package main

import "fmt"

func main() {
	// Exercise 1: Accept explicit secure configuration: predict an edited check: Copy worked example 1 into a scratch pad and change `check(validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil, "target")` to `check(validateTarget("https://cluster.invalid:6443!", "lesson", "owned-lesson") == nil, "target")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `target` because the edited check no longer holds. Restoring the original line brings back the worked observation: the configuration is accepted.

	// Exercise 2: Reject insecure transport: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") == nil, "TLS")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `TLS`; after it the line reads `check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") != nil, "TLS")` again and the configuration is rejected.

	// Exercise 3: Reject ambient context selection: Omit the context name.
	// Expected: Validation rejects the configuration.

	// Exercise 4: Constrain a namespace: Attempt a namespace containing a slash.
	// Expected: Validation rejects it.

	// Exercise 5: Construct a bounded request: Build an HTTPS list request with a live context without sending it.
	// Expected: The method and URL path are correct.

	// Exercise 6: Transfer userinfo rejection: Reject an endpoint embedding userinfo.
	// Expected: The embedded credential form is rejected.

	fmt.Println("Implement the six investigations in your saved pad.")
}
