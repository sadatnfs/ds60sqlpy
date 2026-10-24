package main

import "fmt"

func main() {
	// Exercise 1: Read a successful response: Use a fake transport returning status 200 and body ready.
	// Expected: The client helper returns ready without error.

	// Exercise 2: Reject an HTTP failure status: Return status 404 with a body.
	// Expected: The helper returns an error despite transport success.

	// Exercise 3: Detect an oversized body: Return five bytes with a maximum of four.
	// Expected: The helper rejects the response.

	// Exercise 4: Honor cancellation: Cancel the context before invoking the fake transport.
	// Expected: The returned error matches context.Canceled.

	// Exercise 5: Allow exact size: Return four bytes with a maximum of four.
	// Expected: The helper accepts all four bytes.

	// Exercise 6: Transfer an empty body: Return 200 with an empty body under a positive budget.
	// Expected: The transport helper returns an empty string successfully.

	fmt.Println("Implement the six investigations in your saved pad.")
}
