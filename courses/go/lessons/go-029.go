package main

import "fmt"

func main() {
	// Exercise 1: Publish through a channel: change one input: Copy worked example 1 into a scratch pad and change `go func() { ch <- Published{Count: 3, Ready: true} }()` to `go func() { ch <- Published{Count: 4, Ready: true} }()`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `publication` because `v.Ready && v.Count == 3` no longer holds. Restoring the original line brings back the worked observation: the reader observes count 3 and ready true.

	// Exercise 2: Publish through closure: debug a regression: A regression changed one token in worked example 2, so one line now reads `go func() { n = 8; close(done) }()`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `close publication`; after it the line reads `go func() { n = 7; close(done) }()` again and the reader observes 7.

	// Exercise 3: Publish an atomic value: Store a complete record in atomic.Value.
	// Expected: The loaded record has count 4.

	// Exercise 4: Retain a previous snapshot: Load a value, then replace the stored value.
	// Expected: The old copy remains 4 and the current value is 5.

	// Exercise 5: Copy reference-containing data: Copy a slice before mutating the original.
	// Expected: The snapshot retains its original first element.

	// Exercise 6: Transfer local construction: Build a result string inside a worker and send the completed value.
	// Expected: The reader receives ready:3.

	fmt.Println("Implement the six investigations in your saved pad.")
}
