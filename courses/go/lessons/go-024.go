package main

import "fmt"

func main() {
	// Exercise 1: Join a produced result: Start a goroutine computing 6 times 7 and receive its result.
	// Expected: The received value is 42.

	// Exercise 2: Wait for several tasks: Start three tasks that signal a buffered completion channel and wait for all of them.
	// Expected: Exactly three completion markers are received.

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
