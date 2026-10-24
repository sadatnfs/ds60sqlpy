package main

import "fmt"

func main() {
	// Exercise 1: Inspect the current target: Read runtime target identifiers.
	// Expected: Both identifiers are nonempty.

	// Exercise 2: Validate a supported deployment tuple: Check linux/amd64 and linux/arm64 against an explicit target set.
	// Expected: Both tuples are admitted.

	// Exercise 3: Refuse an unsupported tuple: Check an unrelated target against the same set.
	// Expected: The unsupported target is rejected.

	// Exercise 4: Model stop-accepting before drain: Transition a service state from accepting to draining to stopped.
	// Expected: No new work is admitted once draining begins.

	// Exercise 5: Retain unfinished work evidence: Apply a shutdown budget that ends before two tasks finish.
	// Expected: The remaining task count stays visible.

	// Exercise 6: Transfer deterministic version metadata: Format a version and source revision into a build label.
	// Expected: The result is lesson/1.0 revision=abc123.

	fmt.Println("Implement the six investigations in your saved pad.")
}
