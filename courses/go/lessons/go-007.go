package main

import "fmt"

func main() {
	// Exercise 1: Count two units: change one input: Copy worked example 1 into a scratch pad and change `text := "A🙂"` to `text := "A🙂!"`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `text units` because `len(text) == 5 && utf8.RuneCountInString(text) == 2` no longer holds. Restoring the original line brings back the worked observation: there are 5 bytes and 2 runes.

	// Exercise 2: Edit a copied byte slice: debug a regression: A regression changed one token in worked example 2, so one line now reads `data[1] = 'b'`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `copy edit`; after it the line reads `data[0] = 'b'` again and the original is cat and the new string is bat.

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
