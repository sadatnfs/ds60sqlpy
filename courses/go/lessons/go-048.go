package main

import "fmt"

func main() {
	// Exercise 1: Converge from a different state: Reconcile owned UID u1 from count 1 to desired 3.
	// Expected: The count becomes 3 with one write.

	// Exercise 2: Repeat without duplicate writes: Run the same desired state twice.
	// Expected: Only the first call writes.

	// Exercise 3: Refuse a replacement object: Supply expected UID old while observed UID is new.
	// Expected: No write occurs and an ownership error is returned.

	// Exercise 4: Preserve state on invalid intent: Request a negative count.
	// Expected: The operation fails without mutation.

	// Exercise 5: Cancel before new work: Pass an already-canceled context.
	// Expected: No write occurs and cancellation is retained.

	// Exercise 6: Transfer restart reasoning: Copy the converged durable state into a new controller invocation.
	// Expected: The restarted invocation makes no additional write.

	fmt.Println("Implement the six investigations in your saved pad.")
}
