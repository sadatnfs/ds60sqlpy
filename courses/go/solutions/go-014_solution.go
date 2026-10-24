package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func clamp(x int) int {
	if x < 0 {
		return 0
	}
	if x > 10 {
		return 10
	}
	return x
}
func mutantClamp(x int) int {
	if x < 0 {
		return 0
	}
	if x > 9 {
		return 9
	}
	return x
}

func main() {
	// Build a named table
	{
		cases := []struct{ in, want int }{{-2, 0}, {4, 4}, {12, 10}}
		for _, tc := range cases {
			check(clamp(tc.in) == tc.want, "clamp table")
		}
	}

	// Include exact endpoints
	{
		check(clamp(0) == 0 && clamp(10) == 10, "endpoints")
	}

	// Check idempotence
	{
		for _, x := range []int{-2, 4, 12} {
			check(clamp(clamp(x)) == clamp(x), "idempotence")
		}
	}

	// Reject a plausible mutant
	{
		check(clamp(10) != mutantClamp(10), "mutant rejected")
	}

	// Cover a range invariant
	{
		for x := -20; x <= 20; x++ {
			v := clamp(x)
			check(v >= 0 && v <= 10, "range invariant")
		}
	}

	// Transfer a fresh regression
	{
		check(clamp(11) == 10, "upper regression")
	}
	fmt.Println("All lesson checks passed.")
}
