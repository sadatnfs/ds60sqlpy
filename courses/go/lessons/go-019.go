package main

import "fmt"

func main() {
	// Exercise 1: Decode a typed object: change one input: Copy worked example 1 into a scratch pad and change ``err := json.Unmarshal([]byte(`{"name":"sample","count":3}`), &c)`` to ``err := json.Unmarshal([]byte(`{"name":"sample","count":4}`), &c)``. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `typed JSON` because `err == nil && c.Name == "sample" && c.Count == 3` no longer holds. Restoring the original line brings back the worked observation: the fields become sample and 3.

	// Exercise 2: Reject an unknown property: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(d.Decode(&c) == nil, "unknown field")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `unknown field`; after it the line reads `check(d.Decode(&c) != nil, "unknown field")` again and decoding returns an error.

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
