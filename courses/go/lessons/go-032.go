package main

import "fmt"

func main() {
	// Exercise 1: Escape HTML data: predict an edited check: Copy worked example 1 into a scratch pad and change `check(t.Execute(&b, "<script>alert(1)</script>") == nil, "render")` to `check(t.Execute(&b, "<script>alert(1)</script>") != nil, "render")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `render` because the edited check no longer holds. Restoring the original line brings back the worked observation: angle brackets become escaped text.

	// Exercise 2: Encode a query value: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(err != nil && decoded == original && encoded != original, "query")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `query`; after it the line reads `check(err == nil && decoded == original && encoded != original, "query")` again and decoding recovers the original string.

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
