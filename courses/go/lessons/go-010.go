package main

import "fmt"

func main() {
	// Exercise 1: Dispatch through behavior: change one input: Copy worked example 1 into a scratch pad and change `var v Valuer = Counter{N: 3}` to `var v Valuer = Counter{N: 4}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `interface dispatch` because `v.Value() == 3` no longer holds. Restoring the original line brings back the worked observation: calling Value returns 3.

	// Exercise 2: Mutate through a method: debug a regression: A regression changed one token in worked example 2, so one line now reads `c := Counter{N: 4}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `pointer receiver`; after it the line reads `c := Counter{N: 3}` again and its value becomes 5.

	// Exercise 3: Trace a value receiver: Call a value-receiver helper that increments only its receiver copy.
	// Expected: The returned value is 4 but the original remains 3.

	// Exercise 4: Expose typed nil: Put a nil pointer to Counter inside an empty interface.
	// Expected: The interface is not nil.

	// Exercise 5: Use safe dynamic inspection: Assert that an interface containing a string is an int with comma-ok.
	// Expected: The assertion reports false without panicking.

	// Exercise 6: Transfer substitutability: Implement a second Valuer type returning a fixed value and use the same consuming helper.
	// Expected: Both implementations can be read through one contract.

	fmt.Println("Implement the six investigations in your saved pad.")
}
