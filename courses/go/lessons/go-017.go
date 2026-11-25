package main

import "fmt"

func main() {
	// Exercise 1: Copy a stream: change one input: Copy worked example 1, change `n, err := io.Copy(&out, strings.NewReader("alpha"))` to `n, err := io.Copy(&out, strings.NewReader("alpha!"))` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `copy` because `err == nil && n == 5 && out.String() == "alpha"` no longer holds.

	// Exercise 2: Require a full record: debug a regression: A one-token regression in worked example 2 makes a line read `n, err := io.ReadFull(strings.NewReader("ab!"), buf)`. Repair it without changing the check.
	// Expected: The defective run panics with `partial record`; after restoring `n, err := io.ReadFull(strings.NewReader("ab"), buf)`, two bytes arrive and ErrUnexpectedEOF is returned.

	// Exercise 3: Bound visible input: Read at most three bytes from abcdef.
	// Expected: The visible result is abc.

	// Exercise 4: Detect excess data: Read a four-byte budget for a three-byte maximum.
	// Expected: A four-byte result proves the maximum was exceeded.

	// Exercise 5: Preserve an empty stream: Copy an empty reader to a buffer.
	// Expected: The count is zero and there is no error.

	// Exercise 6: Transfer exact framing: Read a two-byte header followed by a three-byte payload.
	// Expected: The header is AB and payload is xyz.

	fmt.Println("Implement the six investigations in your saved pad.")
}
