package main

import "fmt"

func main() {
	// Exercise 1: Build a named table: change one input: Copy worked example 1 into a scratch pad and change `cases := []struct{ in, want int }{{-2, 0}, {4, 4}, {12, 10}}` to `cases := []struct{ in, want int }{{-2, 1}, {4, 4}, {12, 10}}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `clamp table` because `clamp(tc.in) == tc.want` no longer holds. Restoring the original line brings back the worked observation: the outputs are 0, 4 and 10.

	// Exercise 2: Include exact endpoints: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(clamp(1) == 0 && clamp(10) == 10, "endpoints")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `endpoints`; after it the line reads `check(clamp(0) == 0 && clamp(10) == 10, "endpoints")` again and both endpoints are preserved.

	// Exercise 3: Check idempotence: Apply clamp twice to values -2, 4 and 12.
	// Expected: Applying it twice gives the same result as once.

	// Exercise 4: Reject a plausible mutant: Compare the correct clamp with a mutant that incorrectly caps at 9.
	// Expected: Input 10 distinguishes them.

	// Exercise 5: Cover a range invariant: Check all integer inputs from -20 through 20.
	// Expected: Every result lies between 0 and 10.

	// Exercise 6: Transfer a fresh regression: Retain input 11 as a regression for an implementation that forgets the upper cap.
	// Expected: The result is 10.

	fmt.Println("Implement the six investigations in your saved pad.")
}
