package main

import (
	"fmt"
	"iter"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func makeCounter() func() int { n := 0; return func() int { n++; return n } }
func mapInts(items []int, f func(int) int) []int {
	out := make([]int, len(items))
	for i, x := range items {
		out[i] = f(x)
	}
	return out
}
func visit(limit int, f func(int) bool) {
	for i := 1; i <= limit; i++ {
		if !f(i) {
			return
		}
	}
}
func countTo(limit int, produced *int) iter.Seq[int] {
	return func(yield func(int) bool) {
		for i := 1; i <= limit; i++ {
			*produced++
			if !yield(i) {
				return
			}
		}
	}
}

func main() {
	// Capture a changing variable
	{
		factor := 2
		multiply := func(x int) int { return factor * x }
		factor = 3
		check(multiply(4) == 12, "capture variable")
	}

	// Create independent counters
	{
		a, b := makeCounter(), makeCounter()
		check(a() == 1 && a() == 2 && b() == 1, "independent closures")
	}

	// Inject a transformation
	{
		v := mapInts([]int{1, 2, 3}, func(x int) int { return 2 * x })
		check(len(v) == 3 && v[0] == 2 && v[2] == 6, "callback")
	}

	// Stop a visitor early
	{
		count := 0
		visit(5, func(x int) bool { count++; return x < 3 })
		check(count == 3, "early stop")
	}

	// Handle an empty traversal
	{
		count := 0
		visit(0, func(x int) bool { count++; return true })
		check(count == 0, "empty callback")
	}

	// Transfer the visitor to a range-over-func iterator
	{
		produced := 0
		got := []int{}
		for x := range countTo(5, &produced) {
			got = append(got, x)
			if x == 2 {
				break
			}
		}
		check(len(got) == 2 && got[0] == 1 && got[1] == 2 && produced == 2, "range over func")
	}
	fmt.Println("All lesson checks passed.")
}
