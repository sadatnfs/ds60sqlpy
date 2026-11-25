package main

import "fmt"

func main() {
	// Exercise 1: Read an in-memory file: change one input: Copy worked example 1, change `files := fstest.MapFS{"data/input.txt": &fstest.MapFile{Data: []byte("red\n")}}` to `files := fstest.MapFS{"data/input.txt!": &fstest.MapFile{Data: []byte("red\n")}}` and predict the failure before running; then restore the line.
	// Expected: The edited run panics with `file read` because `err == nil && string(v) == "red\n"` no longer holds.

	// Exercise 2: Observe a missing file: debug a regression: Break one line of worked example 2 so `errors.Is(err, fs.ErrNotExist)` fails, then trace the panic back to it.
	// Expected: Your defect panics with `missing file`; undoing it restores the worked observation: the error matches fs.ErrNotExist.

	// Exercise 3: Reject traversal syntax: Validate ../private and data/input.txt.
	// Expected: The traversal path is invalid and the relative data path is valid.

	// Exercise 4: Walk only owned entries: Walk a two-file in-memory tree and count regular files.
	// Expected: Exactly two files are observed.

	// Exercise 5: Separate empty content from absence: Read an existing zero-byte file.
	// Expected: Reading succeeds and returns zero bytes.

	// Exercise 6: Transfer confinement to a real directory with os.Root: Open an owned temporary directory as an os.Root, create item.txt through it, then try to open ../outside.txt through the same root.
	// Expected: item.txt is created inside the root and the escaping name is rejected.

	fmt.Println("Implement the six investigations in your saved pad.")
}
