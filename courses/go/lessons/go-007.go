package main

import "fmt"

func main() {
	// Exercise 1: Count two units: change one input: Copy worked example 1, change `text := "A🙂"` to `text := "A🙂!"` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `text units` because `len(text) == 5 && utf8.RuneCountInString(text) == 2` no longer holds.

	// Exercise 2: Edit a copied byte slice: debug a regression: A one-token regression in worked example 2 makes a line read `data[1] = 'b'`. Repair it without changing the check.
	// Expected: The defective run panics with `copy edit`; after restoring `data[0] = 'b'`, the original is cat and the new string is bat.

	// Exercise 3: Reject malformed encoding: Build a string from the single byte 0xff.
	// Expected: UTF-8 validation returns false.

	// Exercise 4: Slice by rune position: Convert A and the emoji to runes and retain the second rune.
	// Expected: The resulting string is the intact emoji.

	// Exercise 5: Separate combining forms: Count runes in e followed by a combining accent.
	// Expected: There are 2 runes even though it can display as one character.

	// Exercise 6: Transfer a whitespace policy: Trim surrounding whitespace from a label without changing its internal space.
	// Expected: The result is blue sky.

	fmt.Println("Implement the six investigations in your saved pad.")
}
