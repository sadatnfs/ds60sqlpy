package main

import "fmt"

func main() {
	// Exercise 1: Distinguish zero from missing: change one input: Copy worked example 1, change `m := map[string]int{"zero": 0}` to `m := map[string]int{"zero": 1}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `presence` because `a == b && okA && !okB` no longer holds.

	// Exercise 2: Build a frequency table: debug a regression: A one-token regression in worked example 2 makes a line read `for _, v := range []string{"red!", "blue", "red"} {`. Repair it without changing the check.
	// Expected: The defective run panics with `counts`; after restoring `for _, v := range []string{"red", "blue", "red"} {`, red has count 2 and blue has count 1.

	// Exercise 3: Sort report keys: Extract keys beta and alpha and sort them.
	// Expected: The first output key is alpha.

	// Exercise 4: Observe assigned map aliasing: Assign a map to another variable and update through the second.
	// Expected: Both names observe the changed entry.

	// Exercise 5: Remove an absent key safely: Delete a missing key and then an existing key.
	// Expected: The map ends empty without a failure.

	// Exercise 6: Transfer nil read behavior: Read a missing key from a nil map.
	// Expected: The value is 0 and presence is false.

	fmt.Println("Implement the six investigations in your saved pad.")
}
