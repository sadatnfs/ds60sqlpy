package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Observe shared storage
	{
		values := []int{1, 2, 3}
		view := values[:2]
		view[0] = 9
		check(values[0] == 9, "alias")
	}

	// Make an independent copy
	{
		values := []int{1, 2, 3}
		cloned := append([]int(nil), values...)
		cloned[0] = 9
		check(values[0] == 1 && cloned[0] == 9, "copy")
	}

	// Restrict append capacity
	{
		values := []int{1, 2, 3}
		limited := values[:1:1]
		grown := append(limited, 8)
		check(values[1] == 2 && grown[1] == 8, "capacity boundary")
	}

	// Inspect a truncated copy
	{
		dst := make([]int, 2)
		n := copy(dst, []int{4, 5, 6})
		check(n == 2 && dst[1] == 5, "copy length")
	}

	// Grow an empty slice
	{
		var values []int
		check(values == nil && len(values) == 0, "nil slice")
		values = append(values, 7)
		check(len(values) == 1 && values[0] == 7, "append nil")
	}

	// Transfer array semantics
	{
		a := [2]int{1, 2}
		b := a
		b[0] = 9
		check(a[0] == 1 && b[0] == 9, "array copy")
	}
	fmt.Println("All lesson checks passed.")
}
