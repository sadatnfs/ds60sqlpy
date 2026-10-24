package main

import "fmt"

func main() {
	// Exercise 1: Plan a missing child: Observe no child for a desired replica count of 3.
	// Expected: The action is create.

	// Exercise 2: Plan a changed child: Observe an existing child with count 2 while desired is 3.
	// Expected: The action is update.

	// Exercise 3: Make convergence a no-op: Observe an existing child already at count 3.
	// Expected: The action is none.

	// Exercise 4: Reject invalid desired state: Supply a negative desired count.
	// Expected: The planner returns invalid.

	// Exercise 5: Simulate a converging step: Start at count 1, apply the planned update to 3 and plan again.
	// Expected: The next plan is none.

	// Exercise 6: Transfer scale-to-zero: Request zero for an existing child with count 2.
	// Expected: The planner requests update, then converges at zero.

	fmt.Println("Implement the six investigations in your saved pad.")
}
