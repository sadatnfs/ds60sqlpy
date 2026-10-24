package main

import "fmt"

func main() {
	// Exercise 1: Admit a required read: Allow get on pods in the lesson namespace.
	// Expected: The request is admitted by the local rule model.

	// Exercise 2: Reject an unneeded mutation: Try delete against the read-only rule.
	// Expected: The request is rejected.

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
