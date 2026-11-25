package main

import "fmt"

func main() {
	// Exercise 1: Register cleanup responsibility: predict an edited check: Copy worked example 1, change `check(finalAction(false, false, false, true) == "add-finalizer", "register")` to `check(finalAction(true, false, false, true) == "add-finalizer", "register")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `register` even though `finalAction(false, false, false, true) == "add-finalizer"` still holds.

	// Exercise 2: Retain a healthy object: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(finalAction(true, true, false, true) == "reconcile", "normal")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `normal`; after restoring `check(finalAction(false, true, false, true) == "reconcile", "normal")`, the action is reconcile.

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
