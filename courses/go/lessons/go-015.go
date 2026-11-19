package main

import "fmt"

func main() {
	// Exercise 1: Reuse an element contract: change one input: Copy worked example 1 into a scratch pad and change `a, okA := first([]int{4, 5})` to `a, okA := first([]int{5, 5})`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `generic first` because `okA && okB && a == 4 && b == "red"` no longer holds. Restoring the original line brings back the worked observation: the results are 4 and red with presence true.

	// Exercise 2: Handle a generic empty value: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(v != 0 && !ok, "empty generic")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `empty generic`; after it the line reads `check(v == 0 && !ok, "empty generic")` again and the result is zero with presence false.

	// Exercise 3: Preserve stable uniqueness: Deduplicate 2, 1, 2 while preserving first occurrence.
	// Expected: The result is 2 then 1.

	// Exercise 4: Admit a named underlying type: Sum two values of a named Count type.
	// Expected: The result is Count(7).

	// Exercise 5: Test the empty sum identity: Sum an empty int64 slice.
	// Expected: The result is int64 zero.

	// Exercise 6: Transfer equality semantics: Deduplicate strings with different case.
	// Expected: Red and red remain distinct.

	fmt.Println("Implement the six investigations in your saved pad.")
}
