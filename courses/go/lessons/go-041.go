package main

import "fmt"

func main() {
	// Exercise 1: Accept explicit secure configuration: predict an edited check: Copy worked example 1, change `check(validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil, "target")` to `check(validateTarget("https://cluster.invalid:6443!", "lesson", "owned-lesson") == nil, "target")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `target` even though `validateTarget("https://cluster.invalid:6443", "lesson", "owned-lesson") == nil` still holds.

	// Exercise 2: Reject insecure transport: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") == nil, "TLS")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `TLS`; after restoring `check(validateTarget("http://cluster.invalid", "lesson", "owned-lesson") != nil, "TLS")`, the configuration is rejected.

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
