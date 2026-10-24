package main

import "fmt"

func main() {
	// Exercise 1: Preserve a cause: Wrap ErrMissing with a record-reading context.
	// Expected: errors.Is still recognizes ErrMissing.

	// Exercise 2: Reject text equality: Construct two separate errors with the same wording.
	// Expected: Their identities differ.

	// Exercise 3: Inspect a typed boundary: Return a LimitError carrying an allowed maximum and inspect it with errors.As.
	// Expected: The extracted limit is 3.

	// Exercise 4: Handle successful parsing: Parse valid integer text and check error before value use.
	// Expected: The result is 42 and the error is nil.

	// Exercise 5: Classify invalid parsing: Parse malformed integer text and inspect its NumError.
	// Expected: The typed parse error is present.

	// Exercise 6: Transfer joined failures: Join missing and permission errors and inspect both causes.
	// Expected: Both sentinels remain discoverable.

	fmt.Println("Implement the six investigations in your saved pad.")
}
