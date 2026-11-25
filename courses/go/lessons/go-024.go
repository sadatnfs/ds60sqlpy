package main

import "fmt"

func main() {
	// Exercise 1: Join a produced result: change one input: Copy worked example 1, change `go func() { result <- 6 * 7 }()` to `go func() { result <- 7 * 7 }()` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `goroutine result` because `<-result == 42` no longer holds.

	// Exercise 2: Wait for several tasks: debug a regression: A one-token regression in worked example 2 makes a line read `for i := 1; i < 3; i++ {`. Repair it without changing the check.
	// Expected: The defective run panics with `joined tasks`; after restoring `for i := 0; i < 3; i++ {`, exactly three completion markers are received.

	// Exercise 3: Keep state task-local: Have two goroutines compute from explicit arguments.
	// Expected: The results sum to 13.

	// Exercise 4: Establish a start boundary: Block a worker on a start channel, then release it.
	// Expected: The worker returns ready only after release.

	// Exercise 5: Reject premature completion: Keep a worker blocked behind a start channel and test whether its result is available before release.
	// Expected: The result is unavailable before release and equals 1 afterward.

	// Exercise 6: Transfer deterministic aggregation: Collect squares from four workers and sum them in the receiving goroutine.
	// Expected: The sum is 30.

	fmt.Println("Implement the six investigations in your saved pad.")
}
