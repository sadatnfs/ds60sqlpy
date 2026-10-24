package main

import "fmt"

func main() {
	// Exercise 1: Decode a typed object: Decode a name and count into Config.
	// Expected: The fields become sample and 3.

	// Exercise 2: Reject an unknown property: Use a strict decoder on an object with an unexpected extra field.
	// Expected: Decoding returns an error.

	// Exercise 3: Detect a second document: Decode two adjacent JSON objects and check whether another value exists.
	// Expected: A second value is observable, so the single-document contract fails.

	// Exercise 4: Confirm exact completion: Decode one object, then require EOF.
	// Expected: The second decode returns io.EOF.

	// Exercise 5: Preserve a large integer token: Use UseNumber while decoding 9007199254740993 into any.
	// Expected: The exact decimal token is retained.

	// Exercise 6: Transfer domain validation: Decode a negative count successfully, then reject it as a domain error.
	// Expected: JSON syntax is valid but count validation fails.

	fmt.Println("Implement the six investigations in your saved pad.")
}
