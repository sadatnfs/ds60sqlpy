package main

import "fmt"

func main() {
	// Exercise 1: Drain before iteration ends: change one input: Copy worked example 1 into a scratch pad and change `ch <- 2` to `ch <- 3`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `drain` because `sum == 5` no longer holds. Restoring the original line brings back the worked observation: both values arrive and the sum is 5.

	// Exercise 2: Distinguish zero from closed: debug a regression: A regression changed one token in worked example 2, so one line now reads `ch <- 1`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `closed presence`; after it the line reads `ch <- 0` again and the first zero has ok true; the second has ok false.

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
