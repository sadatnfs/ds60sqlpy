package main

import (
	"errors"
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func twice(x int) int { return 2 * x }
func positiveArea(w, h int) (int, error) {
	if w <= 0 || h <= 0 {
		return 0, errors.New("positive dimensions required")
	}
	return w * h, nil
}
func reassign(x int) { x = 99 }
func bounds(a, b int) (int, int) {
	if a < b {
		return a, b
	}
	return b, a
}
func total(values ...int) int {
	n := 0
	for _, v := range values {
		n += v
	}
	return n
}

func main() {
	// Implement a pure helper
	{
		check(twice(7) == 14 && twice(0) == 0, "twice")
	}

	// Return an explicit failure
	{
		area, err := positiveArea(3, 4)
		check(err == nil && area == 12, "area")
		_, err = positiveArea(0, 4)
		check(err != nil, "invalid area")
	}

	// Trace copied scalar state
	{
		n := 5
		reassign(n)
		check(n == 5, "value copy")
	}

	// Return both ordered values
	{
		low, high := bounds(9, 2)
		check(low == 2 && high == 9, "bounds")
	}

	// Test a variadic identity
	{
		check(total() == 0 && total(1, 2, 3) == 6, "variadic")
	}

	// Transfer the contract
	{
		value, err := positiveArea(3, -1)
		check(err != nil && value == 0, "negative dimension")
	}
	fmt.Println("All lesson checks passed.")
}
