package main

import "fmt"

func main() {
	// Exercise 1: Implement a pure helper: predict an edited check: Copy worked example 1 into a scratch pad and change `check(twice(7) == 14 && twice(0) == 0, "twice")` to `check(twice(8) == 14 && twice(0) == 0, "twice")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `twice` because the edited check no longer holds. Restoring the original line brings back the worked observation: the results are 14 and 0.

	// Exercise 2: Return an explicit failure: debug a regression: A regression changed one token in worked example 2, so one line now reads `_, err = positiveArea(1, 4)`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `invalid area`; after it the line reads `_, err = positiveArea(0, 4)` again and 3 by 4 returns 12; zero width returns an error.

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
