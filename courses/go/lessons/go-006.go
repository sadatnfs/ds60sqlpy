package main

import "fmt"

func main() {
	// Exercise 1: Distinguish zero from missing: change one input: Copy worked example 1 into a scratch pad and change `m := map[string]int{"zero": 0}` to `m := map[string]int{"zero": 1}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `presence` because `a == b && okA && !okB` no longer holds. Restoring the original line brings back the worked observation: both values are 0, but only zero is present.

	// Exercise 2: Build a frequency table: debug a regression: A regression changed one token in worked example 2, so one line now reads `for _, v := range []string{"red!", "blue", "red"} {`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `counts`; after it the line reads `for _, v := range []string{"red", "blue", "red"} {` again and red has count 2 and blue has count 1.

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
