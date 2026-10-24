package main

import "fmt"

func main() {
	// Exercise 1: Mutate through a pointer: Create an integer 4 and increment it through a helper receiving its address.
	// Expected: The caller value becomes 5.

	// Exercise 2: Return a live value: Return a pointer to a local integer initialized to 7.
	// Expected: The returned pointer remains valid and reads 7.

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
