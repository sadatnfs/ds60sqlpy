package main

import "fmt"

func main() {
	// Exercise 1: Decode desired and observed replicas: Decode a fixture requesting 3 replicas with 2 ready.
	// Expected: Desired is 3 while ready is 2.

	// Exercise 2: Distinguish omitted from explicit zero: Decode one absent replicas field and one replicas zero.
	// Expected: Only the explicit zero has a non-nil pointer.

	// Exercise 3: Separate name and incarnation: Construct two objects sharing name but having different UIDs.
	// Expected: Their names match but identities differ.

	// Exercise 4: Keep namespaces in a key: Build keys for the same name in two namespaces.
	// Expected: The keys are different.

	// Exercise 5: Treat versions as opaque: Store a nonnumeric resourceVersion token and compare it for equality.
	// Expected: The exact token is retained.

	// Exercise 6: Transfer readiness reasoning: Compare desired 3 with ready 3 and then ready 2.
	// Expected: Only the equal complete state satisfies this simplified predicate.

	fmt.Println("Implement the six investigations in your saved pad.")
}
