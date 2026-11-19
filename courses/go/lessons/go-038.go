package main

import "fmt"

func main() {
	// Exercise 1: Accept a current version: change one input: Copy worked example 1 into a scratch pad and change `err := versionUpdate(&s, "a", 3, "b")` to `err := versionUpdate(&s, "a", 4, "b")`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `current update` because `err == nil && s.Value == 3 && s.Version == "b"` no longer holds. Restoring the original line brings back the worked observation: the value changes and token becomes b.

	// Exercise 2: Reject a stale version: debug a regression: A regression changed one token in worked example 2, so one line now reads `s := Versioned{Value: 4, Version: "b"}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `conflict`; after it the line reads `s := Versioned{Value: 3, Version: "b"}` again and conflict is returned and value stays unchanged.

	// Exercise 3: Reread before retry: Read the current token after conflict and recompute an increment.
	// Expected: The new value is based on current state.

	// Exercise 4: Keep opaque tokens opaque: Use token rv:opaque rather than an integer.
	// Expected: Equality-based update succeeds.

	// Exercise 5: Retain another field: Update the value of an object that also carries an owner label, using its current token.
	// Expected: The value and token change while the owner label is unchanged.

	// Exercise 6: Transfer bounded conflict handling: Try the same stale token twice and count conflicts.
	// Expected: Both attempts conflict and neither changes state.

	fmt.Println("Implement the six investigations in your saved pad.")
}
