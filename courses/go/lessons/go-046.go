package main

import "fmt"

func main() {
	// Exercise 1: Accept a valid range: change one input: Copy worked example 1 into a scratch pad and change `d := admit("r1", 3, 5, false)` to `d := admit("r2", 3, 5, false)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `allow` because `d.Allowed && d.UID == "r1"` no longer holds. Restoring the original line brings back the worked observation: the decision allows the request.

	// Exercise 2: Reject a negative value: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(!d.Allowed && d.Reason == "", "negative")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `negative`; after it the line reads `check(!d.Allowed && d.Reason != "", "negative")` again and the decision denies it with a reason.

	// Exercise 3: Check the exact upper boundary: Validate counts 5 and 6 against maximum 5.
	// Expected: Five is allowed and six is denied.

	// Exercise 4: Preserve request identity: Validate a request and inspect the response UID.
	// Expected: The exact request UID is copied.

	// Exercise 5: Keep dry-run side effects absent: Evaluate the same allowed request once in dry-run mode and once for real.
	// Expected: Both decisions allow the request; only the real evaluation records a side effect.

	// Exercise 6: Transfer missing identity refusal: Evaluate a request lacking its UID.
	// Expected: The decision is denied.

	fmt.Println("Implement the six investigations in your saved pad.")
}
