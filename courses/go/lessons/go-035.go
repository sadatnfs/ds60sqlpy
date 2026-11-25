package main

import "fmt"

func main() {
	// Exercise 1: Decode desired and observed replicas: change one input: Copy worked example 1, change `"replicas":3` to `"replicas":4` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `spec status` because `err == nil && d.Spec.Replicas != nil && *d.Spec.Replicas == 3 && d.Status.Ready == 2` no longer holds.

	// Exercise 2: Distinguish omitted from explicit zero: diagnose an edited check: A careless edit rewrote the check in worked example 2 as ``check(json.Unmarshal([]byte(`{"spec":{"replicas":1}}`), &b) == nil, "decode")``. Explain the failure, then restore it.
	// Expected: The defective run panics with `presence`; after restoring ``check(json.Unmarshal([]byte(`{"spec":{"replicas":0}}`), &b) == nil, "decode")``, only the explicit zero has a non-nil pointer.

	// Exercise 3: Separate name and incarnation: Decode two objects that share namespace and name but carry different UIDs.
	// Expected: Their names match but their identities differ.

	// Exercise 4: Keep namespaces in a key: Build keys with one function for the same name in two namespaces.
	// Expected: The key is alpha/demo for the first object and differs from the second object's key.

	// Exercise 5: Treat versions as opaque: Decode resourceVersion tokens 10 and 9 and compare them as the strings they are.
	// Expected: Both tokens are retained exactly; they differ, and string order even places 10 before 9, so only equality is meaningful.

	// Exercise 6: Transfer readiness reasoning: Apply one readiness predicate to desired 3 with ready 3 and then ready 2.
	// Expected: Only the equal complete state satisfies this simplified predicate.

	fmt.Println("Implement the six investigations in your saved pad.")
}
