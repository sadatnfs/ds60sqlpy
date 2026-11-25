package main

import "fmt"

func main() {
	// Exercise 1: Reuse an element contract: change one input: Copy worked example 1, change `a, okA := first([]int{4, 5})` to `a, okA := first([]int{5, 5})` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `generic first` because `okA && okB && a == 4 && b == "red"` no longer holds.

	// Exercise 2: Handle a generic empty value: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(v != 0 && !ok, "empty generic")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `empty generic`; after restoring `check(v == 0 && !ok, "empty generic")`, the result is zero with presence false.

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
