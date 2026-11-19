package main

import "fmt"

func main() {
	// Exercise 1: Observe shared storage: change one input: Copy worked example 1 into a scratch pad and change `view[0] = 9` to `view[1] = 9`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `alias` because `values[0] == 9` no longer holds. Restoring the original line brings back the worked observation: the original first element becomes 9.

	// Exercise 2: Make an independent copy: debug a regression: A regression changed one token in worked example 2, so one line now reads `values := []int{2, 2, 3}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `copy`; after it the line reads `values := []int{1, 2, 3}` again and the original stays 1 while the copy starts 9.

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
