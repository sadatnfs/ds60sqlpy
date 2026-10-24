package main

import "fmt"

func main() {
	// Exercise 1: Observe shared storage: Take the first two elements of 1, 2, 3 and change the first through the slice.
	// Expected: The original first element becomes 9.

	// Exercise 2: Make an independent copy: Copy 1, 2, 3 into a new slice and mutate that copy.
	// Expected: The original stays 1 while the copy starts 9.

	// Exercise 3: Restrict append capacity: Take values[:1:1] and append 8.
	// Expected: The original second element remains 2.

	// Exercise 4: Inspect a truncated copy: Copy three source elements into a length-two destination.
	// Expected: Exactly two elements are copied.

	// Exercise 5: Grow an empty slice: Append 7 to a nil slice.
	// Expected: The result has length 1 and value 7.

	// Exercise 6: Transfer array semantics: Copy a fixed array and mutate the copy.
	// Expected: The original array remains unchanged.

	fmt.Println("Implement the six investigations in your saved pad.")
}
