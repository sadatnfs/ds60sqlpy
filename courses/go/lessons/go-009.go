package main

import "fmt"

func main() {
	// Exercise 1: Mutate through a pointer: change one input: Copy worked example 1, change `n := 4` to `n := 5` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `pointer mutation` because `n == 5` no longer holds.

	// Exercise 2: Return a live value: diagnose an edited check: A careless edit rewrote the check in worked example 2 as `check(*p != 7, "returned pointer")`. Explain the failure, then restore it.
	// Expected: The defective run panics with `returned pointer`; after restoring `check(*p == 7, "returned pointer")`, the returned pointer remains valid and reads 7.

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
