package main

import "fmt"

func main() {
	// Exercise 1: Register cleanup responsibility: Inspect a normal object without the controller finalizer.
	// Expected: The next action is add-finalizer.

	// Exercise 2: Retain a healthy object: Inspect a nondeleting object whose finalizer is present.
	// Expected: The action is reconcile.

	// Exercise 3: Clean before releasing deletion: Inspect a deleting object with outstanding owned cleanup.
	// Expected: The action is cleanup.

	// Exercise 4: Remove only after success: Inspect a deleting object with confirmed cleanup.
	// Expected: The action is remove-own-finalizer.

	// Exercise 5: Refuse ownership mismatch: Inspect a resource whose observed UID no longer matches the owned UID.
	// Expected: The action is ownership-error.

	// Exercise 6: Transfer preservation of other finalizers: Remove only lesson.example/cleanup from two entries.
	// Expected: The unrelated entry remains.

	fmt.Println("Implement the six investigations in your saved pad.")
}
