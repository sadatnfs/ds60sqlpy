package main

import "fmt"

func main() {
	// Exercise 1: Register cleanup responsibility: predict an edited check: Copy worked example 1 into a scratch pad and change `check(finalAction(false, false, false, true) == "add-finalizer", "register")` to `check(finalAction(true, false, false, true) == "add-finalizer", "register")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `register` because the edited check no longer holds. Restoring the original line brings back the worked observation: the next action is add-finalizer.

	// Exercise 2: Retain a healthy object: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(finalAction(true, true, false, true) == "reconcile", "normal")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `normal`; after it the line reads `check(finalAction(false, true, false, true) == "reconcile", "normal")` again and the action is reconcile.

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
