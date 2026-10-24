package main

import "fmt"

func main() {
	// Exercise 1: Drain before iteration ends: Buffer 2 and 3, close and sum the channel.
	// Expected: Both values arrive and the sum is 5.

	// Exercise 2: Distinguish zero from closed: Send zero, close, then receive twice with comma-ok.
	// Expected: The first zero has ok true; the second has ok false.

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
