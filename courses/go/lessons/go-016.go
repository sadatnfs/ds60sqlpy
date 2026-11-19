package main

import "fmt"

func main() {
	// Exercise 1: Capture a changing variable: change one input: Copy worked example 1 into a scratch pad and change `factor = 3` to `factor = 4`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `capture variable` because `multiply(4) == 12` no longer holds. Restoring the original line brings back the worked observation: the closure uses the new factor 3.

	// Exercise 2: Create independent counters: diagnose an edited check: A careless edit changed the check in worked example 2 so that it reads `check(a() != 1 && a() == 2 && b() == 1, "independent closures")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.
	// Expected: Before the repair the program panics with `independent closures`; after it the line reads `check(a() == 1 && a() == 2 && b() == 1, "independent closures")` again and the first returns 1 then 2; the second starts at 1.

	// Exercise 3: Inject a transformation: Map a doubling callback over 1, 2 and 3.
	// Expected: The result is 2, 4 and 6.

	// Exercise 4: Stop a visitor early: Visit 1 through 5 and stop after observing 3.
	// Expected: Exactly three values are visited.

	// Exercise 5: Handle an empty traversal: Visit an empty range with a callback that would increment a count.
	// Expected: The callback is never invoked.

	// Exercise 6: Transfer the visitor to a range-over-func iterator: Range over an iter.Seq[int] that yields 1 through 5, append each value, and break after 2.
	// Expected: The loop collects 1 and 2, and the iterator produces exactly two values.

	fmt.Println("Implement the six investigations in your saved pad.")
}
