package main

import "fmt"

func main() {
	// Exercise 1: Distinguish zero from missing: Read present key zero and absent key missing with comma-ok.
	// Expected: Both values are 0, but only zero is present.

	// Exercise 2: Build a frequency table: Count red, blue and red.
	// Expected: red has count 2 and blue has count 1.

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
