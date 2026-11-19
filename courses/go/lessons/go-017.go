package main

import "fmt"

func main() {
	// Exercise 1: Copy a stream: change one input: Copy worked example 1 into a scratch pad and change `n, err := io.Copy(&out, strings.NewReader("alpha"))` to `n, err := io.Copy(&out, strings.NewReader("alpha!"))`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `copy` because `err == nil && n == 5 && out.String() == "alpha"` no longer holds. Restoring the original line brings back the worked observation: five bytes are copied and output is alpha.

	// Exercise 2: Require a full record: debug a regression: A regression changed one token in worked example 2, so one line now reads `n, err := io.ReadFull(strings.NewReader("ab!"), buf)`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `partial record`; after it the line reads `n, err := io.ReadFull(strings.NewReader("ab"), buf)` again and two bytes arrive and ErrUnexpectedEOF is returned.

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
