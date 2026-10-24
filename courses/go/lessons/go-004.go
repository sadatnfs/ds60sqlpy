package main

import "fmt"

func main() {
	// Exercise 1: Implement a pure helper: Implement twice and check inputs 7 and 0.
	// Expected: The results are 14 and 0.

	// Exercise 2: Return an explicit failure: Implement positiveArea that rejects a nonpositive dimension.
	// Expected: 3 by 4 returns 12; zero width returns an error.

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
