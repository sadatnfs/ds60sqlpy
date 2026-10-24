package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func plan(wanted int, exists bool, current int) string {
	if wanted < 0 {
		return "invalid"
	}
	if !exists {
		return "create"
	}
	if wanted != current {
		return "update"
	}
	return "none"
}

func main() {
	// Plan a missing child
	{
		check(plan(3, false, 0) == "create", "missing child")
	}

	// Plan a changed child
	{
		check(plan(3, true, 2) == "update", "changed child")
	}

	// Make convergence a no-op
	{
		check(plan(3, true, 3) == "none", "converged")
	}

	// Reject invalid desired state
	{
		check(plan(-1, true, 2) == "invalid", "invalid intent")
	}

	// Simulate a converging step
	{
		current := 1
		check(plan(3, true, current) == "update", "first plan")
		current = 3
		check(plan(3, true, current) == "none", "second plan")
	}

	// Transfer scale-to-zero
	{
		check(plan(0, true, 2) == "update" && plan(0, true, 0) == "none", "zero scale")
	}
	fmt.Println("All lesson checks passed.")
}
