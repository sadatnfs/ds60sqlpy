package main

import "fmt"

func main() {
	// Exercise 1: Read an in-memory file: Read data/input.txt containing red and a newline.
	// Expected: The bytes decode to red followed by a newline.

	// Exercise 2: Observe a missing file: Read absent.txt from an empty filesystem.
	// Expected: The error matches fs.ErrNotExist.

	// Exercise 3: Reject traversal syntax: Validate ../private and data/input.txt.
	// Expected: The traversal path is invalid and the relative data path is valid.

	// Exercise 4: Walk only owned entries: Walk a two-file in-memory tree and count regular files.
	// Expected: Exactly two files are observed.

	// Exercise 5: Separate empty content from absence: Read an existing zero-byte file.
	// Expected: Reading succeeds and returns zero bytes.

	// Exercise 6: Transfer a subtree boundary: Create an fs.Sub rooted at data and read only its relative item.
	// Expected: item.txt is readable within the logical subtree.

	fmt.Println("Implement the six investigations in your saved pad.")
}
