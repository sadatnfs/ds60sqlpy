package main

import "fmt"

func main() {
	// Exercise 1: Compare two divisions: change one input: Copy worked example 1 into a scratch pad and change `a := 7 / 2` to `a := 8 / 2`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `division` because `a == 3 && b == 3.5` no longer holds. Restoring the original line brings back the worked observation: the results are 3 and 3.5.

	// Exercise 2: Expose narrowing: debug a regression: A regression changed one token in worked example 2, so one line now reads `n := 261`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `narrowing`; after it the line reads `n := 260` again and the narrowed value is 4.

	// Exercise 3: Preserve a wide product: Multiply two explicitly int64 values of 50000.
	// Expected: The product is 2500000000.

	// Exercise 4: Check approximate arithmetic: Add floating variables 0.1 and 0.2 and compare with a 1e-15 tolerance.
	// Expected: The absolute difference from 0.3 is below 1e-15.

	// Exercise 5: Reject invalid numeric text: Parse the text 12x as a base-ten signed integer.
	// Expected: Parsing returns a non-nil error.

	// Exercise 6: Transfer signed division: Divide -7 by 2 and compute its remainder.
	// Expected: The quotient is -3 and the remainder is -1.

	fmt.Println("Implement the six investigations in your saved pad.")
}
