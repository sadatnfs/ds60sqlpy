package main

import "fmt"

func main() {
	// Exercise 1: Drain before iteration ends: change one input: Copy worked example 1, change `ch <- 2` to `ch <- 3` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `drain` because `sum == 5` no longer holds.

	// Exercise 2: Distinguish zero from closed: debug a regression: A one-token regression in worked example 2 makes a line read `ch <- 1`. Repair it without changing the check.
	// Expected: The defective run panics with `closed presence`; after restoring `ch <- 0`, the first zero has ok true; the second has ok false.

	// Exercise 3: Use sender ownership: Run a producer sending 1 and 2 before closing output.
	// Expected: The consumer receives exactly two values.

	// Exercise 4: Inspect bounded buffering: Fill a channel of capacity two without a receiver.
	// Expected: Its buffered length is two.

	// Exercise 5: Disable a nil select arm: Select between nil and a ready closed channel.
	// Expected: Only the ready arm can proceed.

	// Exercise 6: Transfer independent message storage: Send a copied slice, then mutate its original.
	// Expected: The received copy stays 1.

	fmt.Println("Implement the six investigations in your saved pad.")
}
