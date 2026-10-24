package main

import "fmt"

func main() {
	// Exercise 1: Cancel a child: Create a cancelable context and cancel it.
	// Expected: Err returns context.Canceled.

	// Exercise 2: Propagate parent cancellation: Derive a child and cancel its parent.
	// Expected: Both contexts become canceled.

	// Exercise 3: Keep child cancellation local: Cancel a child of a live parent.
	// Expected: The child is canceled; the parent is unchanged.

	// Exercise 4: Test an expired deadline: Construct a context with a deadline at Unix time zero.
	// Expected: Err is context.DeadlineExceeded.

	// Exercise 5: Refuse already canceled work: Call a helper that checks its context before calculation.
	// Expected: It returns cancellation without a result.

	// Exercise 6: Transfer successful work: Use the same helper with a live context.
	// Expected: It returns 8 without error.

	fmt.Println("Implement the six investigations in your saved pad.")
}
