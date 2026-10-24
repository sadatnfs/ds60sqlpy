package main

import "fmt"

func main() {
	// Exercise 1: Escape HTML data: Render script-like text with html/template.
	// Expected: Angle brackets become escaped text.

	// Exercise 2: Encode a query value: Encode a value containing ampersand and equals characters.
	// Expected: Decoding recovers the original string.

	// Exercise 3: Reject traversal grammar: Compare ../outside with reports/item.txt.
	// Expected: Only the second path is lexically local.

	// Exercise 4: Apply a byte budget: Compare three-byte and five-byte values against maximum four.
	// Expected: Only the smaller value fits.

	// Exercise 5: Compare fixed-size values: Compare equal and unequal four-byte values.
	// Expected: The helper returns 1 for equal and 0 for unequal.

	// Exercise 6: Transfer a reviewed action set: Allow read and list, then inspect read and exec.
	// Expected: read is accepted and exec is rejected.

	fmt.Println("Implement the six investigations in your saved pad.")
}
