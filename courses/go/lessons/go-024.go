package main

import "fmt"

func main() {
	// Exercise 1: Join a produced result: change one input: Copy worked example 1 into a scratch pad and change `go func() { result <- 6 * 7 }()` to `go func() { result <- 7 * 7 }()`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `goroutine result` because `<-result == 42` no longer holds. Restoring the original line brings back the worked observation: the received value is 42.

	// Exercise 2: Wait for several tasks: debug a regression: A regression changed one token in worked example 2, so one line now reads `for i := 1; i < 3; i++ {`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `joined tasks`; after it the line reads `for i := 0; i < 3; i++ {` again and exactly three completion markers are received.

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
