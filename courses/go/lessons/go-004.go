package main

import "fmt"

func main() {
	// Exercise 1: Implement a pure helper: predict an edited check: Copy worked example 1, change `check(twice(7) == 14 && twice(0) == 0, "twice")` to `check(twice(8) == 14 && twice(0) == 0, "twice")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `twice` even though `twice(7) == 14 && twice(0) == 0` still holds.

	// Exercise 2: Return an explicit failure: debug a regression: A one-token regression in worked example 2 makes a line read `_, err = positiveArea(1, 4)`. Repair it without changing the check.
	// Expected: The defective run panics with `invalid area`; after restoring `_, err = positiveArea(0, 4)`, 3 by 4 returns 12; zero width returns an error.

	// Exercise 3: Trace copied scalar state: Pass 5 to a helper that reassigns its local parameter.
	// Expected: The caller still holds 5.

	// Exercise 4: Return both ordered values: Implement bounds for two integers.
	// Expected: Inputs 9 and 2 return 2 then 9.

	// Exercise 5: Test a variadic identity: Sum zero inputs and then 1, 2 and 3.
	// Expected: The results are 0 and 6.

	// Exercise 6: Transfer the contract: Call the area helper with a negative height and keep the error visible.
	// Expected: The invalid domain is rejected before returning a usable area.

	fmt.Println("Implement the six investigations in your saved pad.")
}
