package main

import "fmt"

func main() {
	// Exercise 1: Mutate through a pointer: change one input: Copy worked example 1 into a scratch pad and change `n := 4` to `n := 5`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `pointer mutation` because `n == 5` no longer holds. Restoring the original line brings back the worked observation: the caller value becomes 5.

	// Exercise 2: Return a live value: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(*p != 7, "returned pointer")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `returned pointer`; after it the line reads `check(*p == 7, "returned pointer")` again and the returned pointer remains valid and reads 7.

	// Exercise 3: Guard absence: Represent an optional integer with a nil pointer and inspect it without dereferencing.
	// Expected: The pointer is absent.

	// Exercise 4: Allocate a zero target: Use new(int) and compare pointer presence with its stored value.
	// Expected: The pointer is non-nil and its target is 0.

	// Exercise 5: Separate copy and target: Copy the integer behind a pointer, then change the original target.
	// Expected: The copied integer remains 3 while the target becomes 9.

	// Exercise 6: Transfer an optional update: Implement setIfPresent so a nil pointer is a harmless no-op and a present pointer changes.
	// Expected: The absent call returns false; the present value becomes 8.

	fmt.Println("Implement the six investigations in your saved pad.")
}
