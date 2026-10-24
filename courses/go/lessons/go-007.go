package main

import "fmt"

func main() {
	// Exercise 1: Count two units: Inspect A followed by a smiling face.
	// Expected: There are 5 bytes and 2 runes.

	// Exercise 2: Edit a copied byte slice: Convert cat to bytes, replace c with b and retain the original.
	// Expected: The original is cat and the new string is bat.

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
