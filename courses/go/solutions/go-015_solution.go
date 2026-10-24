package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Count int
type Integer interface{ ~int | ~int64 }

func first[T any](items []T) (T, bool) {
	if len(items) == 0 {
		var zero T
		return zero, false
	}
	return items[0], true
}
func unique[T comparable](items []T) []T {
	seen := map[T]bool{}
	out := []T{}
	for _, x := range items {
		if !seen[x] {
			seen[x] = true
			out = append(out, x)
		}
	}
	return out
}
func sumInts[T Integer](items []T) T {
	var out T
	for _, x := range items {
		out += x
	}
	return out
}

func main() {
	// Reuse an element contract
	{
		a, okA := first([]int{4, 5})
		b, okB := first([]string{"red", "blue"})
		check(okA && okB && a == 4 && b == "red", "generic first")
	}

	// Handle a generic empty value
	{
		v, ok := first([]int{})
		check(v == 0 && !ok, "empty generic")
	}

	// Preserve stable uniqueness
	{
		v := unique([]int{2, 1, 2})
		check(len(v) == 2 && v[0] == 2 && v[1] == 1, "unique order")
	}

	// Admit a named underlying type
	{
		check(sumInts([]Count{3, 4}) == Count(7), "underlying type")
	}

	// Test the empty sum identity
	{
		check(sumInts([]int64{}) == 0, "generic identity")
	}

	// Transfer equality semantics
	{
		v := unique([]string{"Red", "red", "Red"})
		check(len(v) == 2, "case policy")
	}
	fmt.Println("All lesson checks passed.")
}
