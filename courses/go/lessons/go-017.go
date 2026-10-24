package main

import "fmt"

func main() {
	// Exercise 1: Copy a stream: Copy alpha from a strings.Reader into bytes.Buffer.
	// Expected: Five bytes are copied and output is alpha.

	// Exercise 2: Require a full record: Read exactly four bytes from a two-byte source.
	// Expected: Two bytes arrive and ErrUnexpectedEOF is returned.

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
